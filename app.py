#import remote_pdb
from flask import Flask
from flask import request
from flask import jsonify
from urllib import parse        # check if url is valid
from .citation import Citation   # provides a way to save quote and upload json
from lib.citeit_quote_context.url import URL    # lookup quotes
import settings
import boto3
import json
import os

#remote_pdb.RemotePdb('0.0.0.0', 5858).set_trace()


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI


@app.route('/hello')
def hello_world(event, context):
    return 'This is the CiteIt api!'


@app.route('/', methods=['GET', 'POST'])
def post_url():
    """
        Lookup citations referenced by specified url
        Find 500 characters before and after
        Pass data to Citation class
        Save contextual data to database and
        Upload json file to cloud

        USAGE: http://localhost:5000/post/url/https://www.citeit.net/
    """
    saved_citations = {}

    # GET URL Parameter
    if request.method == "POST":
        url_string = request.args.post('url', '')
    else:
        url_string = request.args.get('url', '')

    # Check if URL is of a valid format
    parsed_url = parse.urlparse(url_string)
    is_url = bool(parsed_url.scheme)

    # Lookup Citations for this URL and Save
    if not is_url:
        saved_citations['error'] = "Specify a valid URL of the form: https://api.citeit.net/?url=http://example.com/page_name"
    else:
        url = URL(url_string)
        citations = url.citations()
        for n, citation in enumerate(citations):
            print(n, ": saving citation.")
            c = Citation(citation)  # lookup citation
            c.save()                # save citation to database

            # Set JSON values
            quote_json = {}
            quote_json['citing_quote'] = c.data['citing_quote']
            quote_json['sha256'] = c.data['sha256']
            quote_json['citing_url'] = c.data['citing_url']
            quote_json['cited_url'] = c.data['cited_url']
            quote_json['citing_context_before'] = c.data['citing_context_before']
            quote_json['cited_context_before'] = c.data['cited_context_before']
            quote_json['citing_context_after'] = c.data['citing_context_after']
            quote_json['cited_context_after'] = c.data['cited_context_after']
            quote_json['cited_quote'] = c.data['cited_quote']


            # Save JSON to local file
            print("Saving Json locally ..")
            json_file = json.dumps(quote_json)
            json_filename = ''.join([c.data['sha256'], '.json'])
            json_full_filepath = os.path.join(settings.JSON_FILE_PATH, 'quote', 'sha256', '0.3', json_filename)
            with open(json_full_filepath, 'w+') as f:
                f.write(json_file)

            print("Saving Json to S3 ..")
            shard = json_filename[:2]
            remote_path= ''.join(["quote/sha256/", settings.VERSION_NUM, "/", shard, "/", json_filename])
            
	    # Upload JSON to Amazon S3
	    s3 = boto3.resource('s3')
	    s3.meta.client.upload_file(
	        json_file,
	        settings.AMAZON_S3_BUCKET,
	        remote_path,
	        ExtraArgs={'ContentType':"application/json", 'ACL': "public-read"}
	    )


	    """
            s3_resource = boto3.resource('s3', endpoint_url=settings.AMAZON_S3_ENDPOINT,
                                         config=boto3.session.Config(signature_version='s3v4'),
                                         aws_access_key_id=settings.AMAZON_ACCESS_KEY,
                                         aws_secret_access_key=settings.AMAZON_SECRET_KEY,
                                         )
            shard = json_filename[:2]
            file_key = ''.join(["quote/sha256/", settings.VERSION_NUM, "/", shard, "/", json_filename])
            s3_resource.Bucket(settings.AMAZON_S3_BUCKET).put_object(
                Key=file_key,
                Body=open(json_full_filepath, 'rb'),
                ContentType="application/json"
            )
            object_acl = s3_resource.ObjectAcl(settings.AMAZON_S3_BUCKET, file_key)
            object_acl.put(ACL='public-read')
	    """

            # Output simple summary
            saved_citations[c.data['sha256']] = c.data['citing_quote']
            print(c.data['sha256'], ' ', c.data['citing_quote'])


    return jsonify(saved_citations)


if __name__ == '__main__':
    app.run()

# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from flask import Flask
from flask import request
from flask import jsonify
from urllib import parse        # check if url is valid
from citation import Citation   # provides a way to save quote and upload json
from lib.citeit_quote_context.url import URL
from lib.citeit_quote_context.canonical_url import Canonical_URL
from lib.citeit_quote_context.document import Document
from lib.citeit_quote_context.quote import Quote
import urllib3
import settings
import boto3
import json
import os

VERSION = "0.4"


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = VERSION



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/about')
def about():
    return 'Hello, This is the CiteIt.net api! version: ' + VERSION

@app.route('/', methods=['GET', 'POST'])
@app.route('/v' + VERSION + '/url/', methods=['GET', 'POST'])
def post_url():
    """
        Lookup citations referenced by specified url
        Find 500 characters before and after
        Pass data to Citation class
        Save contextual data to database and
        Upload json file to cloud

        USAGE: http://localhost:5000/v0.4/url?url=https://www.citeit.net/
    """
    saved_citations = {}


    # GET URL Parameter
    if request.method == "POST":
        url_string = request.form.get('url', '')
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
            c.db_save()             # save citation to database

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
            quote_json['hashkey'] = c.data['hashkey']

            # Save JSON to local file
            print("Saving Json locally ..")
            json_file = json.dumps(quote_json)
            json_filename = ''.join([c.data['sha256'], '.json'])
            json_full_filepath = os.path.join(settings.JSON_FILE_PATH, json_filename)
            print("Full Filepath x1: " + json_full_filepath)
            with open(json_full_filepath, 'w+') as f:
                f.write(json_file)

            print("Saving Json to S3 ..")
            shard = json_filename[:2]
            remote_path= ''.join(["quote/sha256/0.4/", str(shard), "/", json_filename])
            print("JSON Path: " + json_file)
            print("Remote path: " + remote_path)

            # Upload JSON to Amazon S3
            session = boto3.Session(
                aws_access_key_id=settings.AMAZON_ACCESS_KEY,
                aws_secret_access_key=settings.AMAZON_SECRET_KEY
            )
            
            s3 = session.resource('s3')
            s3.meta.client.upload_file(
                Filename=json_full_filepath,
                Bucket=settings.AMAZON_S3_BUCKET,
	        Key=remote_path,
	        ExtraArgs={'ContentType':"application/json", 'ACL': "public-read"},
            )

            # Output simple summary
            saved_citations[c.data['sha256']] = c.data['citing_quote']
            print(c.data['sha256'], ' ', c.data['hashkey'], ' ', c.data['citing_quote'])

    return jsonify(saved_citations)

@app.route('/v' + VERSION + '/url/hashkeys', methods=['GET'])
def quote_hashkeys():
    # Get hashkeys for every quote on a page:

    citing_url = request.args.get('url', '')
    url = URL(citing_url)
    citations_list = url.citations_list_dict()
    quotes = []

    for quote in citations_list:
        q = Quote(  quote['citing_quote'],
                    quote['citing_url'],
                    quote['cited_url']
        )

        citing_quote = quote['citing_quote']  #q.citing_quote()
        hashkey = q.hashkey()
        quotes.append({citing_quote: hashkey})

    return jsonify(quotes)



@app.route('/v' + VERSION + '/url/canonical-url', methods=['GET'])
def canonical_url():
    # Lookup the Canonical URL of a page
    url = request.args.get('url', '')
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    html = r.data
    canonical_url = Canonical_URL(html, url)
    return  jsonify({url : canonical_url.citeit_url()})


@app.route('/url/text-version', methods=['GET'])
@app.route('/v' + VERSION + '/url/text-version', methods=['GET'])
def document_text_version():
    url = request.args.get('url', '')
    d = Document(url)
    return d.text()

@app.route('/v' + VERSION + '/url/meta-data', methods=['GET'])
def document_meta_data():
    url = request.args.get('url', '')
    verbose_view = request.args.get('verbose', True)
    d = Document(url)
    document_data = d.data(verbose_view=verbose_view)
    return  jsonify(document_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


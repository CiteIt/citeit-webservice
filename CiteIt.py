from flask import Flask
from flask import request
from urllib import parse        # check if url is valid
from citation import Citation   # provides a way to save quote and upload json
from lib.citeit_quote_context.url import URL    # lookup quotes
import settings

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI


@app.route('/')
def hello_world():
    return 'This is the CiteIt api!'


@app.route('/post/url', methods=['GET', 'POST'])
def post_url():
    """
        Lookup citations referenced by specified url
        Find 500 characters before and after
        Pass data to Citation class
        Save contextual data to database and
        Upload json file to cloud

        USAGE: http://localhost:5000/post/url/https://www.neotext.net/demo/
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
    if is_url:
        url = URL(url_string)
        citations = url.citations()
        for n, citation in enumerate(citations):
            print(n, ": saving citation.")
            c = Citation(citation)
            c.save()
            print(c.data['sha256'], ' ', c.data['citing_quote'])
            saved_citations[c.data['sha256']] = c.data['citing_quote']
    else:
        print("Error: Not a valid url")

    return ""


if __name__ == '__main__':
    app.run()

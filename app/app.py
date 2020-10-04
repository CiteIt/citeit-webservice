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
from lib.citeit_quote_context.misc.utils import publish_file
from lib.citeit_quote_context.misc.utils import escape_json
import urllib3
import hashlib
import settings
import json
import os

import logging


WEBSERVICE_VERSION = "0.4"


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = WEBSERVICE_VERSION

ADMINS = ['citeit@openpolitics.com']


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

logging.basicConfig(filename='error.log',level=logging.DEBUG)

if not app.debug:
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(mailhost=('smtp.gmail.com', 465),
                               fromaddr='citeit@openpolitics.com',
                               toaddrs=ADMINS, subject='CiteIt Webserver Error',
                               credentials=('citeit@openpolitics.com', 'FyP3LAYM2TcAQxFBxUbc2shX')
                               )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


@app.route('/about')
def about():
    return 'Hello, This is the CiteIt.net api! version: ' + WEBSERVICE_VERSION

@app.route('/', methods=['GET', 'POST'])
@app.route('/v' + WEBSERVICE_VERSION + '/url/', methods=['GET', 'POST'])
def post_url():
    """
        Lookup citations referenced by specified url
        Find 500 characters before and after
        Pass data to Citation class
        Save contextual data to database and
        Upload json file to cloud

        USAGE: http://localhost:5000/v0.4/url?url=https://www.citeit.net/
    """

    # GET URL Parameters
    if request.method == "POST":
        url_string = request.form.get('url', '')
        format = request.form.get('format', '')
    else:
        url_string = request.args.get('url', '')
        format = request.args.get('format', '')


    if (format == 'list'):
        saved_citations = []  # return full JSON list
    else:
        saved_citations = {}  # return summary dict: sha256: quote


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
            quote_json['citing_quote'] = escape_json(c.data['citing_quote'])
            quote_json['sha256'] = c.data['sha256']
            quote_json['citing_url'] = c.data['citing_url']
            quote_json['cited_url'] = c.data['cited_url']
            quote_json['citing_context_before'] = escape_json(c.data['citing_context_before'])
            quote_json['cited_context_before'] = escape_json(c.data['cited_context_before'])
            quote_json['citing_context_after'] = escape_json(c.data['citing_context_after'])
            quote_json['cited_context_after'] = escape_json(c.data['cited_context_after'])
            quote_json['cited_quote'] = escape_json(c.data['cited_quote'])
            quote_json['hashkey'] = c.data['hashkey']

            # Setting up Json settings locally ..
            json_file = json.dumps(quote_json)
            json_filename = ''.join([c.data['sha256'], '.json'])
            json_full_filepath = os.path.join(settings.JSON_FILE_PATH, json_filename)

            # Setting up Json settings with Cloud"
            shard = json_filename[:2]
            remote_path= ''.join(["quote/sha256/0.4/", str(shard), "/", json_filename])
            print("JSON Path: " + json_file)
            print("Remote path: " + remote_path)

            # Publish JSON to Cloud, save copy locally
            publish_file(
                '',
                json_file,
                json_full_filepath,
                remote_path,
                "application/json"
            )

            if (format == 'list'):
                saved_citations.append(quote_json)
            else:
                # Output simple summary:
                saved_citations[c.data['sha256']] = c.data['citing_quote']
                print(c.data['sha256'], ' ', c.data['hashkey'], ' ', c.data['citing_quote'])

            print("File Uploaded")

    return jsonify(saved_citations)

@app.route('/url/encoding', methods=['GET', 'POST'])
@app.route('/v' + WEBSERVICE_VERSION + '/url/encoding', methods=['GET'])
def url_encoding():

    citing_url = request.args.get('url', '')
    url = URL(citing_url)
    #print(url.doc().encoding_lookup())
    return jsonify({'encoding': url.doc().encoding_lookup()})

@app.route('/url/hashkeys', methods=['GET', 'POST'])
@app.route('/v' + WEBSERVICE_VERSION + '/url/hashkeys', methods=['GET'])
def quote_hashkeys():
    # Get hashkey for each quote of URL:
    # separate by two "\n"

    HASH_ALGORITHM = 'sha256'

    citing_url = request.args.get('url', '')
    url = URL(citing_url)
    citations_list = url.citations_list_dict()
    quotes = []
    output = ''

    for quote in citations_list:
        q = Quote(  quote['citing_quote'],
                    quote['citing_url'],
                    quote['cited_url']
        )

    citing_quote = quote['citing_quote']  #q.citing_quote()
    hashkey = q.hashkey()
    quotes.append({citing_quote: quote['citing_text']})

    output = output + "\n\n" + hashkey

    # hash_method = getattr(hashlib, HASH_ALGORITHM)
    hash_text = hashkey

    return hash_text

@app.route('/v' + WEBSERVICE_VERSION + '/url/canonical-url', methods=['GET'])
def canonical_url():
    # Lookup the Canonical URL of a page
    url = request.args.get('url', '')
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    html = r.data
    canonical_url = Canonical_URL(html, url)
    return  jsonify({url : canonical_url.citeit_url()})


@app.route('/url/text-version', methods=['GET'])
@app.route('/v' + WEBSERVICE_VERSION + '/url/text-version', methods=['GET'])
def document_text_version():
    url = request.args.get('url', '')
    line_separator = request.args.get('line_separator', '')
    timesplits = request.args.get('timesplits')
    if timesplits:
        timesplits = True
    else:
        timesplits = False

    d = Document(url, line_separator, timesplits)

    response = app.make_response(d.text())
    response.mimetype = "text"
    return response


@app.route('/v' + WEBSERVICE_VERSION + '/url/meta-data', methods=['GET'])
def document_meta_data():
    url = request.args.get('url', '')
    verbose_view = request.args.get('verbose', True)
    d = Document(url)
    document_data = d.data(verbose_view=verbose_view)
    return  jsonify(document_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


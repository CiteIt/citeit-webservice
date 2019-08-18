from urllib import parse        # check if url is valid
from citation import Citation   # provides a way to save quote and upload json
from lib.citeit_quote_context.url import URL    # lookup quotes
import settings
import boto3
import json
import os

def lambda_handler(event, context):
    """
        Lookup citations referenced by specified url
        Find 500 characters before and after
        Pass data to Citation class
        Save contextual data to database and
        Upload json file to cloud

        USAGE: http://127.0.0.1:3000/citeit?url=https://www.citeit.net/
    """

    query_params = event['queryStringParameters']
    saved_citations = {}
    url_string = query_params['url']

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
            c.save_all()            # save citation to json & database
            saved_citations[c.json_data()['sha256']] = c.json_data()['citing_quote']

    return {
        "statusCode": 200,
        "body": json.dumps(saved_citations)
    }
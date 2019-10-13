from urllib import parse        # check if url is valid
from citation import Citation   # provides a way to save quote and upload json
from lib.citeit_quote_context.url import URL    # lookup quotes
import settings
import requests
import json

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
    saved_results = {}
    saved_citations = []
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

            saved_citation = {
                'citing_url': c.json_data()['citing_url']
                'cited_url': c.json_data()['cited_url']
                'citing_quote': c.json_data()['citing_quote']
                'sha256': c.json_data()['sha256']
            }
            saved_citations.append(saved_citation)

        saved_results['url'] = url_string
        saved_results['citations'] = saved_citations

        # Notify CiteIt.net when a citation is made:
        # This allows your citation to be collected into a central database
        if settings.NOTIFY_CITEIT:
            # citation_keys enable submitted data be verified with CiteIt.net
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(
                url=settings.NOTIFY_CITEIT_URL,
                data=json.dumps(saved_results),
                headers=headers
            )
            if (r and debug):
                print("Page successfully registered with CiteIt.net: " + citing_url)

    return {
        "statusCode": 200,
        "body": json.dumps(saved_citations)
    }


"""
Example:
https://www.openpolitics.com/articles/the-webs-original-design-1965-would-have-exposed-fake-news-better.html":
[
    {
        "4f61ddb00f1be1416b79b1aa0ecbea12532db1a358584da825546fbec975465f"
        "https://www.openpolitics.com/articles/the-webs-original-design-1965-would-have-exposed-fake-news-better.html",
        "http: // www.theregister.co.uk/2000/10/02/net_builders_kahn_cerf_recognise",
        "As far back as the 1970s Congressman Gore promoted the idea of high speed telecommunications as an engine for both economic growth and the improvement of our educational system.He was the first elected official to grasp the potential of computer communications to have a broader impact than just improving the conduct of science and scholarship."

    }

]
"""
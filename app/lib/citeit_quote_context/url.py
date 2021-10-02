# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.document import Document
from lib.citeit_quote_context.quote import Quote

from lib.citeit_quote_context.misc.utils import publish_file
from lib.citeit_quote_context.misc.utils import escape_json
from citation import Citation 

from bs4 import BeautifulSoup
from functools import lru_cache
from multiprocessing import Pool
from collections import Counter
from flask import jsonify
import time
import settings


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = "0.4"


class URL:
    """
        Looks up all the citations on a publicly-accessible page
        * Uses Document class to download html source for all documents
        * Uses BeautifulSoup to parse html and locate citations,
          creating a text version of each document
        * Uses Quote and QuoteContext to calculate 500 characters
          before and after citation
        * To Save results, iterate through self.citations() and
          save each quote dictionary
    """

    def __init__(self, url):
        self.start_time = time.time()  # measure elapsed execution time
        self.url = url   # user-supplied url

        # get text version of citing page to passed it into load_quote_data()
        self.text = self.text()

    def __str__(self):
        return self.url

    # Document methods imported here so class can make only 1 request per URL
    @lru_cache(maxsize=50)
    def doc(self):
        """ Call Document class """
        return Document(self.url)

    def raw(self):
        """ Return raw data of requested document """
        return self.doc().raw()

    # @lru_cache(maxsize=50)
    def text(self):
        """ Return text version of requested document """
        return self.doc().text()

    def html(self):
        """ If doc_type = 'html', return raw document """
        html = ''
        if (self.doc_type() == 'html'):
            html = self.raw()
        return html

    def doc_type(self):
        """ The class only supports 'html' document types now,
            but could expand to include pdf, word docs and text
        """
        return self.doc().doc_type()

    def citations_list_dict(self):
        """ Create list of quote dictionaries
            to be passed to map function.  Data is supplied
            from urls and text specified in the citing
            document's blockquote and 'cite' attribute."""

        # print("Getting URLs")
        citations_list_dict = []
        soup = BeautifulSoup(self.html(), 'html.parser')

        # Get all blockquote and q tags
        for cite in soup.find_all(['blockquote', 'q']):
            # print("Beautiful Soup: ", cite.get('cite'), cite.text)
            if cite.get('cite'):
                quote = {}
                quote['citing_quote'] = cite.text
                quote['citing_url'] = self.url
                quote['citing_text'] = self.text
                quote['citing_raw'] = self.raw()
                quote['cited_url'] = cite.get('cite')

                citations_list_dict.append(quote)

        return citations_list_dict

    def citation_urls(self):
        """ Returns a list of the urls that have been cited """
        urls = []
        for quote in self.citations_list_dict():
            urls.append(quote['cited_url'])

        return urls

    def citations_list_duplicates(self):
        """
            Test whether a url has been cited multiple times
            Returns a list of duplicate_urls so that these urls can be
            pre-fetched so that the same page isn't clobbered
            (fetched multiple times in parallel)
        """
        duplicate_counter = {}
        duplicate_urls = []

        urls = self.citation_urls()
        duplicate_counter = Counter(urls)
        for cited_url, count in duplicate_counter.items():
            if count > 1:
                duplicate_urls.append(cited_url)

        return duplicate_urls

    def citations(self):
        """ Return a list of Quote Lookup results for all citations on this page
            Uses asychronous pool to achieve parallel processing
            calls load_quote_data() function
            for all values in self.citations_list_dict
            using python 'map' function
        """
        result_list = []

        # Pre-fetch and cache URL if it is found in more than one quote
        # this prevents sources from being clobbered with multiple requests in parallel
        for url in self.citations_list_duplicates():
            d = Document(url)
            d.download_resource()  # request and cache result so parallel requests come from cache

        # Load Quote data in parallel:
        citations_list_dict = self.citations_list_dict()

        pool = Pool(processes=settings.NUM_DOWNLOAD_PROCESSES)
        try:
            result_list = pool.map(load_quote_data, citations_list_dict)

            # Debug: run synchronously
            #for citation_dict in citations_list_dict:
            #    load_quote_data(citation_dict)

        except (NameError, ValueError):
            pass
            # TODO: Add better error handling

        finally:
            pool.close()
            pool.join()

        # Debug: Don't use Pool to Parallelize
        """
        result_list = []
        for c in citations_list_dict:
            result = load_quote_data(c)
            if result:
                result_list.append(result)
        """

        return result_list
    
    def publish_citations(self, format='list'):
        if (format == 'list'):
            saved_citations = []  # return full JSON list
        else:
            saved_citations = {}  # return summary dict: sha256: quote

        for n, citation in enumerate(self.citations()):
            print(n, ": saving citation.")
            c = Citation(citation)  # lookup citation
            #c.db_save()             # save citation to database

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


# ################## Non-class functions #######################


def load_quote_data(quote_keys):
    """ lookup quote data, from keys """
    print("Downloading citation for: " + quote_keys['citing_quote'])
    print("Downloading citation url: " + quote_keys['cited_url'])
    quote = Quote(
                 quote_keys['citing_quote'],
                 quote_keys['citing_url'],
                 quote_keys['cited_url'],
                 quote_keys['citing_text'],  # optional: caching
                 quote_keys['citing_raw']    # optional: caching
             )

    return quote.data()
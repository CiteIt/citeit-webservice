# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.document import Document
from lib.citeit_quote_context.quote import Quote
from bs4 import BeautifulSoup
from functools import lru_cache
from multiprocessing import Pool
from collections import Counter
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


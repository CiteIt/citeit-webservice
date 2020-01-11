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
import time

NUM_DOWNLOAD_PROCESSES = 30

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
        return 'html'  # hard-coded.  Todo: pdf, doc, docx, text

    def citation_url_text(self):
        """ Returns a dictionary of:
                url and
                quote text
            from all blockquote and q tags on this page
        """
        print("Getting URLs")
        cite_urls = {}
        soup = BeautifulSoup(self.html(), 'html.parser')
        for cite in soup.find_all(['blockquote', 'q']):
            if cite.get('cite'):
                cite_urls[cite.get('cite')] = cite.text
        return cite_urls

    def citation_urls(self):
        """ Returns a list of the urls that have been cited """
        urls = []
        for url, text in self.citation_url_text().items():
            urls.append(url)
        return urls

    def citations_list_dict(self):
        """ Create list of quote dictionaries
            to be passed to map function.  Data is supplied
            from urls and text specified in citing
            document's blockquote and 'cite' attribute."""
        citations_list_dict = []
        for cited_url, citing_quote in self.citation_url_text().items():
            quote = {}
            quote['citing_quote'] = citing_quote
            quote['citing_url'] = self.url
            quote['citing_text'] = self.text
            quote['citing_raw'] = self.raw()
            quote['cited_url'] = cited_url
            citations_list_dict.append(quote)
        return citations_list_dict

    def citations(self):
        """ Return a list of Quote Lookup results for all citations on this page
            Uses asychronous pool to achieve parallel processing
            calls load_quote_data() function
            for all values in self.citations_list_dict
            using python 'map' function
        """
        result_list = []
        citations_list_dict = self.citations_list_dict()
        pool = Pool(processes=NUM_DOWNLOAD_PROCESSES)
        #try:
        result_list = pool.map(load_quote_data, citations_list_dict)
        #except ValueError:
        #    # TODO: add better error handling
        #    print("Skipping map value ..")
        pool.close()
        pool.join()
        return result_list


# ################## Non-class functions #######################


def load_quote_data(quote_keys):
    """ lookup quote data, from keys """
    print("Downloading citation for: " + quote_keys['citing_quote'])

    quote = Quote(
                 quote_keys['citing_quote'],
                 quote_keys['citing_url'],
                 quote_keys['cited_url'],
                 quote_keys['citing_text'],  # optional: caching
                 quote_keys['citing_raw']   # optional: caching
             )
    return quote.data()


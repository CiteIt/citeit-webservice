# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.canonical_url import Canonical_URL
from bs4 import BeautifulSoup
from functools import lru_cache
import requests
from datetime import datetime
import ftfy     # Fix bad unicode:  http://ftfy.readthedocs.io/
import re

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2019 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


class Document:
    """ Look up url and compute plain-text version of document
        Use caching to prevent repeated re-querying

        url = 'https://www.openpolitics.com/articles/ted-nelson-philosophy-of-hypertext.html'
        doc = Document(url)
        page_text = doc.text()
    """

    def __init__(self, url	):
        self.url = url  # user supplied URL, may be different from canonical
        self.num_downloads = 0  # count number of times the source is downloaded
        self.request_start = datetime.now()  # time how long request takes
        self.request_stop = None  # Datetime of last download
        self.char_encoding = ''   # character encoding of document, returned by requests library

    # def url(self):
    #    return self.url

    def download_resource(self):
        error = ''
        url = self.url

        try:
            # Use a User Agent to simulate what a Firefox user would see
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1;'
                       ' WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'}
            r = requests.get(url, headers=headers, verify=False)
            print('Downloaded ' + url)
            self.request_stop = datetime.now()
            print("Encoding: %s" % r.encoding )
            self.increment_num_downloads()

            text = r.text
            content = r.content
            encoding = r.encoding
            error = ''

        except requests.HTTPError:
            self.request_stop = datetime.now()

            """ TODO: Add better error tracking """
            error = "document: HTTPError"

        return  {   'text': text,
                    'content': content,
                    'encoding': encoding,
                    'error': error
                }

    @lru_cache(maxsize=20)
    def download(self, convert_to_unicode=False):
        """
            Download the data and update tracking metrics
        """
        return self.download_resource()['text']  # default to blank string

    @lru_cache(maxsize=20)
    def text(self):
        """ Create a text-only version of a document
            In the future, this method would handle other document formats
            such as PDF and Word doc

            Right now, only the HTML conversion is implemented
            I've made comments about possible implementations,
            if you're intested in implementing one of the other methods,

            Idea: https://github.com/skylander86/lambda-text-extractor
        """

        if self.doc_type() == 'html':
            soup = BeautifulSoup(self.html(), "html.parser")
            invisible_tags = ['style', 'script', '[document]', 'head', 'title']
            for elem in soup.findAll(invisible_tags):
                elem.extract()  # hide javascript, css, etc
            text = soup.get_text()
            text = ftfy.fix_text(text)  # fix unicode problems
            text = convert_quotes_to_straight(text)
            text = normalize_whitespace(text)
            return text

        elif self.doc_type == 'pdf':
            # https://github.com/euske/pdfminer/
            return "not implemented"

        elif self.doc_type == 'doc':
            # https://github.com/deanmalmgren/textract
            return "not implemented"

        elif self.doc_type == 'text':
            return self.raw()

        return 'error: no doc_type'

    def doc_type(self):
        """ TODO: Distinguish between html, text, .doc, and pdf"""
        # mime = magic.Magic(mime=True)
        # doc_type = mime.from_file(self.raw())
        # import magic	# https://github.com/ahupp/python-magic
        # return doc_type
        return 'html'  # hardcode to html for now

    @lru_cache(maxsize=20)
    def raw(self, convert_to_unicode=True):
        """
            This method returns the raw, unprocessed data, but
            it is cached for performance reasons, using @lru_cache
        """
        raw = self.download(convert_to_unicode=False)
        if raw:
            return raw
        else:
            return ''

    def html(self):
        """ Get html code, if doc_type = 'html' """
        html = ""
        if self.doc_type() == 'html':
            html = self.raw()
        return html

    @lru_cache(maxsize=20)
    def canonical_url(self):
        """ Web pages may be served from multiple URLs.
            The canonical url is the preferred, permanent URL.
            Use BeautifulSoup to process html and find <link> or <meta> tags.

            Credit: http://pydoc.net/Python/pageinfo/0.40/pageinfo.pageinfo/
        """
        return  Canonical_URL(self.text())

    def citeit_url(self):
        """ Use the canonical_url, if it exists.
            Otherwise, use the user-supplied url.
        """
        if self.canonical_url():
            return self.canonical_url()
        else:
            return self.url

    @lru_cache(maxsize=20)
    def data(self, verbose_view=False):
        """ Dictionary of data associated with URL """
        data = {}
        data['url'] = self.url
        data['canonical_url'] = self.canonical_url()
        data['citeit_url'] = self.citeit_url()
        data['doc_type'] = self.doc_type()
        data['text'] = self.text()
        data['raw'] = self.raw()
        if (verbose_view):
            encoding = self.encoding()
            data['raw_original_encoding'] = self.raw(convert_to_unicode=False)
            data['encoding'] = encoding['encoding']
            data['language'] = encoding['language']
            data['num_downloads'] = self.num_downloads
            data['request_start'] = self.request_start
            data['request_stop'] = self.request_stop
            data['elapsed_time'] = self.elapsed_time()
        return data

    @lru_cache(maxsize=20)
    def encoding(self):
        """ Returns character-encoding for requested document
        """
        resource = self.download_resource()
        if 'encoding' in resource:
            return resource['encoding'].lower()

        return ''


    def request_start(self):
        """ When the Class was instantiated """
        return self.request_start

    def request_stop(self):
        """ Finish time of the last download """
        return self.request_stop

    def elapsed_time(self):
        """ Elapsed time between instantiation and last download """
        return self.request_stop - self.request_start

    def increment_num_downloads(self) -> int:
        """ Increment download counter """
        self.num_downloads = self.num_downloads + 1
        return self.num_downloads

    def num_downloads(self):
        """ Number of time class has downloaded a page.
            This Metric used to tell if class is caching properly
            If it is not, the class will requery the url multiple times
        """
        return self.num_downloads


# ################## Non-class functions #######################

def convert_quotes_to_straight(str):
    """ TODO: I'm cutting corners on typography until I figure out how to
        standardize curly and straight quotes better.

        The problem I'm trying to solve is that a quote may use a different
        style of quote or apostrophe symbol than its source,
        but I still want the quotes match it, so I'm converting
        all quotes and apostrophes to the straight style.
    """
    if str:  # check to see if str isn't empty
        str = str.replace("”", '"')
        str = str.replace("“", '"')
        str = str.replace("’", "'")

        str = str.replace('&#39;', "'")
        str = str.replace('&apos;', "'")
        str = str.replace(u'\xa0', u' ')
        str = str.replace('&\rsquo;', "'")
        str = str.replace('&lsquo;', "'")

        str = str.replace('&rsquo;', '"')
        str = str.replace('&lsquo;', '"')
        str = str.replace("\201C", '"')
        str = str.replace(u"\u201c", "")
        str = str.replace(u"\u201d", "")
    return str

def normalize_whitespace(str):
    """
        Convert multiple spaces and space characters to a single space.
        Trim space at the beginning and end of the string
    """
    if str:  # check to see if str isn't empty
        str = str.replace("&nbsp;", " ")
        str = str.replace(u'\xa0', u' ')
        str = str.strip()               # trim whitespace at beginning and end
        str = re.sub(r'\s+', ' ', str)  # convert multiple spaces into single space
    return str

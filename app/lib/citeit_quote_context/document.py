# Copyright (C) 2015-2020 Tim Langeman and contributors
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
import urllib
import pdftotext      # pdf that have digital text: easier to convert than ocr
# import pytesseract  # ocr library for python
# from pdf2image import convert_from_path
# import glob
# import timeit

from datetime import datetime
from langdetect import detect    # https://www.geeksforgeeks.org/detect-an-unknown-language-using-python/
import ftfy     # Fix bad unicode:  http://ftfy.readthedocs.io/
import re
import os



__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = "0.4"


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

    #def url(self):
    #    return self.url

    def download_resource(self):
        error = ''
        url = self.url

        try:
            # Use a User Agent to simulate what a Firefox user would see
            headers = {'user-agent':'Mozilla / 5.0(Windows NT 6.1;'
                       ' WOW64; rv: 54.0) Gecko/20100101 Firefox/71.0'}

            r = requests.get(url, headers=headers, verify=False)
            # print('Downloaded ' + url)
            self.request_stop = datetime.now()
            # print("Encoding: %s" % r.encoding )
            self.increment_num_downloads()

            text = r.text          # unicode
            content = r.content    # raw
            encoding = r.encoding
            language = detect(r.text)  # https://www.geeksforgeeks.org/detect-an-unknown-language-using-python/
            error = ''
            content_type = r.headers['Content-Type']

        except requests.HTTPError:
            self.request_stop = datetime.now()

            """ TODO: Add better error tracking """
            error = "document: HTTPError"

        return  {   'text': text,         # unicode
                    'unicode': text,
                    'content': content,   # raw
                    'encoding': encoding,
                    'error': error,
                    'language': language,
                    'content_type': content_type
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

        doc_type = self.doc_type()

        if (doc_type == 'html'):
            soup = BeautifulSoup(self.html(), "html.parser")
            invisible_tags = ['style', 'script', '[document]', 'head', 'title']
            for elem in soup.findAll(invisible_tags):
                elem.extract()  # hide javascript, css, etc
            text = soup.get_text()
            text = ftfy.fix_text(text)  # fix unicode problems
            text = convert_quotes_to_straight(text)
            text = normalize_whitespace(text)

            return text

        elif (doc_type == 'pdf'):
            # example: https://demo.citeit.net/2020/06/30/well-behaved-women-seldom-make-history-original-pdf/

            text_filename = urllib.parse.quote_plus(self.url)
            headers = {'user-agent': 'Mozilla / 5.0(Windows NT 6.1;'
                                     ' WOW64; rv: 54.0) Gecko/20100101 Firefox/71.0'}

            # Save PDF to temp file
            r = requests.get(self.url, headers=headers, verify=False)
            open("../downloads/"+ text_filename, 'wb').write(r.content)
            print("Saving text to filename: " + text_filename)


            # Extract text from original pdf file
            with open("../downloads/" + text_filename, 'rb') as f:
                pdf = pdftotext.PDF(f)

            """
            // Credit: https://pypi.org/project/pdftotext/
            
            # How many pages?
            print(len(pdf))

            # Iterate over all the pages
            for page in pdf:
                print(page)

            # Read some individual pages
            print(pdf[0])
            print(pdf[1])
            """

            pdf_text = "\n\n".join(pdf)  # Combine text into single string
            pdf_text = pdf_text.strip()

            # If able to generate text version from digital PDF
            if (len(pdf_text) > 0):

                # Write text version to file:
                text_version_filename = "../text-versions/" +  \
                    os.path.splitext(text_filename)[0] + '.txt'  # replace .pdf file extension


                print("Saving text version to: " + text_version_filename)
                open(text_version_filename, 'w').write(pdf_text)

                return pdf_text

            else: # Generate text version from scanned doc using OCR (more CPU intensive)

                """
                language = 'eng'  # hard coded for now
                input_filename = r"Philosophy-of-Hypertext.pdf"
                pdfs = glob.glob(text_filename)
                output = ''
    
                for pdf_path in pdfs:
                    pages = convert_from_path(pdf_path, 500)
    
                    for pageNum, imgBlob in enumerate(pages):
                        text = pytesseract.image_to_string(imgBlob, lang=language)
                        output_filename = output_file_base + '_page_' + str(pageNum) + '.txt'

                        with open(output_filename, 'w') as the_file:
                            #the_file.write(text)
                            output = output.append(text)
                """

                error_text = "PDF file identified but unable to extract text. OCR Scanning not yet implemented."

                return error_text

        elif (doc_type == 'txt'):
            return self.raw()

        elif (doc_type == 'rtf'):
            return "RTF support not yet implemented.  To implement it see: http://www.gnu.org/software/unrtf/"

        elif (doc_type == 'epub'):
            return "EPub support not yet implemented.  To implement it see: https://github.com/aerkalov/ebooklib"

        elif (doc_type == 'doc'):
            return "Doc support not yet implemented. To implement it see: http://www.winfield.demon.nl/"

        elif (doc_type == 'docx'):
            return "Doc support not yet implemented. To implement it see: https://github.com/ankushshah89/python-docx2txt"

        elif (doc_type == 'pptx'):
            return "Powerpoint support not yet implemented.  To implement it see:  https://python-pptx.readthedocs.org/en/latest/"

        elif (doc_type == 'ps'):
            return "Doc support not yet implemented.  To implement it see: http://www.winfield.demon.nl/"

        elif (doc_type == 'audio/mpeg'):
            return "Doc support not yet implemented.  To implement it see: http://www.winfield.demon.nl/"

        elif (doc_type == 'audio/mpeg'):
            return "MP3 support not yet implemented.  To implement it see: https://pypi.org/project/SpeechRecognition/"

        elif (doc_type == 'audio/ogg'):
            return "OGG support not yet implemented.  To implement it see: https://pypi.org/project/SpeechRecognition/"

        elif (doc_type == 'video/ogg'):
            return "OGG support not yet implemented.  To implement it see: https://pypi.org/project/SpeechRecognition/"

        elif (doc_type == 'wav'):
            return "WAV support not yet implemented.  To implement it see: https://pypi.org/project/SpeechRecognition/"

        elif (doc_type == 'aac'):
            return "AAC support not yet implemented.  To implement it see: https://pypi.org/project/SpeechRecognition/"

        elif (doc_type == 'jpg'):
            return "JPG support not yet implemented.  To implement it see: https://github.com/tesseract-ocr/"

        elif (doc_type == 'png'):
            return "PNG support not yet implemented.  To implement it see: https://github.com/tesseract-ocr/"

        elif (doc_type == 'tiff'):
            return "TIFF support not yet implemented.  To implement it see: https://github.com/tesseract-ocr/"

        elif (doc_type == 'gif'):
            return "GIF support not yet implemented.  To implement it see: https://github.com/tesseract-ocr/"

        elif (doc_type == 'webp'):
            return "WebP support not yet implemented. Does Tesseract support it?  https://github.com/tesseract-ocr/"

        elif (doc_type == 'xls'):
            return "XLS support not yet implemented.  To implement it see: https://pypi.python.org/pypi/xlrd"

        elif (doc_type == 'xlsx'):
            return "XLSX support not yet implemented.  To implement it see: https://pypi.python.org/pypi/xlrd"

        else:
            return 'error: no doc_type: ' + doc_type

    def doc_type(self):
        # Distinguish between html, text, .doc, ppt, and pdf
        content_type = self.download_resource()['content_type']

        if  (   content_type.startswith('text/html') or
                content_type.startswith('application/html')
            ):
            doc_type = 'html'

        elif    content_type.startswith('application/pdf'):
            doc_type = 'pdf'

        elif (  (content_type == 'text/plain') or
                content_type.startswith('text')
            ):
            doc_type = 'txt'

        elif    content_type == 'application/rtf':
            doc_type = 'rtf'

        elif    content_type == 'application/epub+zip':
            doc_type = 'epub'

        elif (  content_type.startswith('application/msword') or
                content_type.startswith('application/vnd.openxmlformats-officedocument.wordprocessingml.document') or
                content_type.startswith('application/vnd.openxmlformats-officedocument.wordprocessingml.template') or
                content_type.startswith('application/vnd.ms-word.document.macroEnabled.12')
            ):
            doc_type = 'doc'

        elif    content_type.startswith('application/vnd.ms-powerpoint'):
            doc_type = 'ppt'

        elif    content_type == 'audio/mpeg':
            doc_type = 'audio/mpeg'

        elif    content_type == 'video/mpeg':
            doc_type = 'video/mpeg'

        elif    content_type == 'audio/ogg':
            doc_type = 'audio/ogg'

        elif    content_type == 'video/ogg':
            doc_type = 'video/ogg'

        elif    content_type == 'application/ogg':
            doc_type = 'audio/ogg'

        elif( content_type == 'audio/wav'):
            doc_type = 'wav'

        elif (content_type == 'audio/aac'):
            doc_type = 'aac'

        elif (  content_type == 'image/jpg' or
                content_type == 'image/jpeg'
            ):
            doc_type = 'jpg'

        elif    content_type == 'image/png':
            doc_type = 'png'

        elif    content_type == 'image/tiff':
            doc_type = 'tiff'

        elif    content_type == 'image/webp':
            doc_type = 'webp'

        elif    content_type == 'image/gif':
            doc_type = 'gif'

        elif    content_type == 'application/vnd.ms-excel':
            doc_type = 'xls'

        elif (  (content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') or
                (content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.template')
            );
            doc_type = 'xlsx'

        else:
             doc_type = 'error: no doc_type: ' + doc_type

        print("Doc Type: " + doc_type)
        return doc_type


    @lru_cache(maxsize=20)
    def raw(self, convert_to_unicode=True):
        """
            This method returns the raw, unprocessed data, but
            it is cached for performance reasons, using @lru_cache
        """
        raw = self.download(convert_to_unicode=convert_to_unicode)
        if raw:
            return raw
        else:
            return ''

    def html(self):
        """ Get html code, if doc_type = 'html' """
        html = ""
        if self.doc_type() == 'html':
            html = self.download_resource()['unicode']   #self.raw()
        return html

    @lru_cache(maxsize=20)
    def canonical_url(self):
        """ Web pages may be served from multiple URLs.
            The canonical url is the preferred, permanent URL.
            Use BeautifulSoup to process html and find <link> or <meta> tags.

            Credit: http://pydoc.net/Python/pageinfo/0.40/pageinfo.pageinfo/
        """

        html = self.html()

        return  Canonical_URL(html).canonical_url()

    def citeit_url(self):
        """ Use the canonical_url, if it exists.
            Otherwise, use the user-supplied url.
        """

        citeit_url = Canonical_URL(self.html()).citeit_url()

        if citeit_url:
            return citeit_url
        else:
            return self.url_without_protocol()

    def url_without_protocol(self):
        return Canonical_URL(self.url).url_without_protocol()

    @lru_cache(maxsize=20)
    def data(self, verbose_view=False):
        """ Dictionary of data associated with URL """
        data = {}
        data['url'] = self.url
        data['canonical_url'] = self.canonical_url()
        data['citeit_url'] = self.citeit_url()
        data['doc_type'] = self.doc_type()
        data['language'] = self.language()

        data['encoding'] = self.encoding()
        data['request_start'] = self.request_start
        data['request_stop'] = self.request_stop
        data['elapsed_time'] = str(self.elapsed_time())
        data['text'] = self.text()
        data['raw'] = self.raw()

        if (verbose_view):
            data['raw_original_encoding'] = self.raw(convert_to_unicode=False)
            data['num_downloads'] = self.num_downloads

        return data

    @lru_cache(maxsize=20)
    def encoding(self):
        """ Returns character-encoding for requested document
        """
        resource = self.download_resource()
        return resource['encoding'].lower()

    def language(self):
        resource = self.download_resource()
        return resource['language']

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

# Copyright (C) 2015-2022 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

#from models import Domain, Document  
from lib.citeit_quote_context.canonical_url import Canonical_URL
from lib.citeit_quote_context.content_type import Content_Type
from lib.citeit_quote_context.transcript import YouTubeTranscript
from lib.citeit_quote_context.transcript import OyezTranscript
from lib.citeit_quote_context.transcript import TwitterTranscript

from lib.citeit_quote_context.canonical_url import url_without_protocol
from lib.citeit_quote_context.misc.utils import publish_file
from lib.citeit_quote_context.misc.utils import fix_encoding
from lib.citeit_quote_context.misc.utils import get_from_cache
from lib.citeit_quote_context.misc.utils import save_file_to_cloud

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib.parse import urlparse

# Used to Generate HTML from Javascript
from requests_html import HTMLSession


from pathlib import Path

import langdetect
import urllib
from urllib.parse import urlparse
from urllib.parse import parse_qs

from datetime import datetime
from langdetect import detect    # https://www.geeksforgeeks.org/detect-an-unknown-language-using-python/
from functools import lru_cache
import ftfy                      # Fix bad unicode:  http://ftfy.readthedocs.io/
import re
import timeit
import settings
import tldextract
import os
import magic
import hashlib


from bs4 import BeautifulSoup  # convert html > text


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2023 Tim Langeman"
__license__ = "MIT"
__version__ = "0.4"

HEADERS = {
   'user-agent': 'Mozilla / 5.0(Windows NT 6.1;'
   ' WOW64; rv: 54.0) Gecko/20100101 Firefox/71.0'
}



class Document:
    """ Look up url and compute plain-text version of document
        Use caching to prevent repeated re-querying

        url = 'https://www.openpolitics.com/articles/ted-nelson-philosophy-of-hypertext.html'
        doc = Document(url)
        page_text = doc.text()
    """

    def __init__(self, url, line_separater='', timesplits='', request_id=0):

        parsed = urlparse(url)
        if (parsed.scheme and parsed.netloc):
            self.url = url  # user supplied URL, may be different from canonical
        else:
            self.url =''


        self.num_downloads = 0  # count number of times the source is downloaded
        self.request_start = datetime.now()  # time how long request takes
        self.request_stop = None  # Datetime of last download

        self.unicode = ''
        self.content = ''      # raw (binary)
        self.encoding = ''     # character encoding of document, returned by requests library
        self.error = ''
        self.language = ''
        self.content_type = ''
        self.line_separater = line_separater
        self.timesplits = timesplits
        self.request_id = request_id

        self.request_dict = {
            'text': '',        # unicode
            'unicode': '',
            'content': '',     # raw
            'encoding': '',
            'error':  '',
            'language': '',
            'content_type': '',
            'request_id': self.request_id,
        }

    def url(self):
        return self.url


    def url_protocol_removed(self):
        return url_without_protocol(self.url)


    @lru_cache(maxsize=500)
    def download_resource(self):

        text = ''  # default to empty string

        # Was this file already downloaded?
        if (len(self.content_type) >= 1):
            print("ALREADY DOWNLOADED.")
            return self.request_dict

        # Is the file cached locally?

        # Does this already exist in database? ***************************************

        file_dict = get_from_cache(self.url_protocol_removed())
        if (len(file_dict['text']) > 0):
            self.request_dict = file_dict
            return file_dict['text']

        # --------- Download file from internet -------------
        try:
            self.increment_num_downloads()
            error = ''
            url = self.url

            # Use a User Agent to simulate what a Firefox user would see
            # session = requests.Sesson()
            session = HTMLSession()

            retry = Retry(connect=5, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            try:
                r = session.get(url, headers=HEADERS, verify=False)

            # Invalid URL
            except requests.exceptions.MissingSchema:
                return {
                    'text': '',  # unicode
                    'unicode': '',
                    'content': '',  # raw
                    'encoding': '',
                    'error': "Connection refused",
                    'language': '',
                    'content_type': ''
                }

            except requests.exceptions.ConnectionError:
                # r.status_code = "Connection refused"
                return {
                    'text': '',       # unicode
                    'unicode': url,
                    'content': url,   # raw
                    'encoding': '',
                    'error': "Connection refused",
                    'language': '',
                    'content_type': ''
                }

            print('Downloaded ' + url )
            self.request_stop = datetime.now()
            print("Encoding: %s" % r.encoding )
            print("num downloads: " + str(self.num_downloads))

            # Correct the Character Encoding


            if url in self.url_encoding_hardcoded():
                hardcoded_encoding = self.url_encoding_hardcoded()[url]
                r.encoding = hardcoded_encoding

            text = r.text

            self.unicode = r.text
            self.content = r.content

            self.encoding = r.encoding
            self.error = error

            try:
                self.language = detect(r.text) # https://www.geeksforgeeks.org/detect-an-unknown-language-using-python/
            except langdetect.lang_detect_exception.LangDetectException:
                self.language = 'en'  # default language


            if 'Content-Type' in r.headers.keys():
                self.content_type = r.headers['Content-Type']
            else:
                self.content_type = 'application/html'
                print(r.headers)    # TODO: Research why content-type is not always set


            print('Content-Type: ' + self.content_type)
            print('Language:     ' + self.language)
            print('Length: ' + str(len(self.content)))
            print("Attempting to save ..  ")

            print(self.unicode)


            ####### Archive a Copy of the Original File ########
            doc_type = self.doc_type()
            print("DocType::: " + doc_type)

            if (doc_type == 'pdf'):
                text = r.content    # file contents

            if (settings.SAVE_DOWNLOADS_TO_FILE):
                write_format = 'w'

                local_filename = self.filename_original()
                remote_path = ''.join(["archive/", self.canonical_url()])
                content_type = self.content_type
                if not content_type:
                    content_type = 'text/html'

                # Create Directory if it doesn't exist
                dirname = os.path.dirname(local_filename)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                if (content_type == 'application/pdf'):
                    text = self.content
                    write_format = 'wb'

                # Archive file
                print("ARCHIVE: local filename----------------------------------")
                print(local_filename)

                my_file = Path(local_filename)
                if my_file.is_file():
                    pass

                else:
                    try:
                        with open(local_filename, write_format) as f:
                            f.write(text)
                    except IsADirectoryError:
                        pass

                # Add file extension if there is none
                filename, file_extension = os.path.splitext(remote_path)
                if not ((file_extension == '.html') or (file_extension == '.htm')):
                    remote_path = os.path.splitext(remote_path)[0] + 'index.html'
                    print("Remote path:")
                    print(remote_path)

                else:
                    remote_path = remote_path + '.' + doc_type

                save_file_to_cloud(local_filename, remote_path, content_type, 'gzip')

            print("Saved original: " + self.filename_original())
            print('Content-Type: ' + self.content_type)
            print('Language:     ' + self.language)
            print('Length: ' + str(len(r.content)))


        except requests.HTTPError:
            self.request_stop = datetime.now()

            """ TODO: Add better error tracking """
            error = "document: HTTPError"

        self.request_dict = {
            'text': text,              # unicode
            'unicode': self.unicode,
            'content': self.content,   # raw
            'encoding': self.encoding,
            'error': self.error,
            'language': self.language,
            'content_type': self.content_type
        }

        # SAVE DB: TODO *********************************

        return self.request_dict

    def download_dict(self):
        return self.request_dict


    @lru_cache(maxsize=20)
    def download(self, convert_to_unicode=False):
        """
            Download the data and update tracking metrics
        """
        # return utf-8 content
        return self.download_resource()['text']  # default to blank string


    def save_db(self):

        # Count Words
        text = self.text()
        words = data.split()
        word_count = len(words)

        """
        # Get Hash of Text Content: used to prevent duplicates
        hash_method = getattr(hashlib, settings.HASH_ALGORITHM)
        try:
            content_hash = hash_method(text.encode(self.encoding)).hexdigest()
        except UnicodeEncodeError:
            content_hash = ''   # TODO: research character encoding error


        # Insert Database Record if it doesn't exist
        document_exists = db.session.query(Document.id).filter_by(content_hash=content_hash, url=self.url).scalar() is not None
        if not document_exists:

            # Lookup Domain ID
            domain = db.query(Domain).filter_by(domain_url=domain_url).first()
            if not domain:          
                domain = Domain(domain_url=domain_url)

            document.insert().values(
                request_id = self.request_id
                , domain_id = domain.id
                , url = self.url
                , content_type = self.content_type
                , title = ''
                , body_binary = self.content
                , body_html = self.html()
                , body_text = text
                , encoding = self.encoding
                , language = self.language
                , word_count = word_count
                , content_hash = content_hash
            ) 
        """

    @lru_cache(maxsize=500)
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
            print("HTML text()")

            # Check Media Provider for transcript: Youtube Video
            if (len(self.media_provider()) > 0):
                supplemental_text = self.supplemental_text()

            soup = BeautifulSoup(self.html(), "html.parser")
            invisible_tags = ['style', 'script', '[document]', 'head', 'title']
            for elem in soup.findAll(invisible_tags):
                elem.extract()  # hide javascript, css, etc
            text = soup.get_text()

            text = fix_encoding(text)
            text = convert_quotes_to_straight(text)
            text = normalize_whitespace(text)

            html_text = text + '\n\n' + self.supplemental_text()
            html_text = html_text.strip()

            # Save a copy of this file: Archive locally and to Cloud
            if (settings.SAVE_DOWNLOADS_TO_FILE):
                local_filename = ''.join(["../transcripts/", self.filename_text()])
                remote_path = ''.join(["transcript/", self.filename_text()])

                publish_file(
                    self.url,
                    html_text,
                    local_filename,
                    remote_path,
                    'text/plain'
                )

            return html_text

        elif (doc_type == 'pdf'):
            # example: https://demo.citeit.net/2020/06/30/well-behaved-women-seldom-make-history-original-pdf/
            # quoted source: https://dash.harvard.edu/bitstream/handle/1/14123819/Vertuous%20Women%20Found.pdf

            pdf = ''
            pdf_text = ''
            start_time = timeit.default_timer()

            try:
                import pdftotext  # convert pdf > text without using ocr
            except ImportError:
                return "Unable to process digital PDF. Pdftotext library not installed."

            print("Start PDF processing ..")
            filename_original = self.filename_original()

            pdf_text = ""

            if (settings.PDF_ENABLED):

                filename_complete = urllib.parse.quote_plus(self.canonical_url_without_protocol())
                local_filename = ''.join(["../downloads/", filename_complete])

                with open(local_filename, 'rb') as f:
                    pdf = pdftotext.PDF(f)

                pdf_text = "\n\n".join(pdf)  # Combine text into single string

            pdf_text = pdf_text.strip()
            pdf_text = fix_encoding(pdf_text)

            """
            // Get other Pages:
                 
            Credit: https://pypi.org/project/pdftotext/
            
            # How many pages?
            print(len(pdf))

            # Iterate over all the pages
            for page in pdf:
                print(page)

            # Read some individual pages
            print(pdf[0])
            print(pdf[1])
            """

            if (settings.PDF_ENABLED):
                # Digital PDF with digitally extractable text: https://dash.harvard.edu/bitstream/handle/1/14123819/Vertuous%20Women%20Found.pdf
                if (len(pdf_text) > 0):
                    local_filename = self.filename_text()
                    remote_path = ''.join(["transcript/pdf/", self.filename_text()])

                    print("PUBLISH FILE (PDF):  " + local_filename)
                    print("PUBLISH REMOTE PATH: " + remote_path )

                    publish_file(
                        self.url,
                        pdf_text,
                        local_filename,
                        remote_path,
                        'text/plain'
                    )

                    return pdf_text

                # OCR: Generate text version from scanned doc using OCR (more CPU intensive)
                else:  # example: https://faculty.washington.edu/rsoder/EDLPS579/DostoevskyGrandInquisitor.pdf

                    try:
                        from pdf2image import convert_from_path
                        import pytesseract  # ocr library for python
                        import glob
                    except ImportError:
                        return "Unable to run OCR to generate PDF from scanned image.  Pdf2impage, Pytesseract not installed for Docker"

                    pdf_output = ''
                    language = 'eng'

                    pdfs = glob.glob(filename_original)
                    print("PDF globs")

                    filename_complete = urllib.parse.quote_plus(self.canonical_url_without_protocol()) + ".txt"

                    for original_pdf_path in pdfs:
                        pages = convert_from_path(filename_original, 500)
                        print("PDFs converted.  Now enumerating ..")

                        for pageNum, imgBlob in enumerate(pages):

                            print("Page: " + str(pageNum))
                            filename_page = urllib.parse.quote_plus(self.canonical_url_without_protocol()) + ".txt" + '@@-page-' + str(pageNum).zfill(4) + '.txt'

                            # Use OCR to convert image > text
                            text = pytesseract.image_to_string(imgBlob, language)
                            text = fix_encoding(text)

                            pdf_output = pdf_output + ' ' + text

                            # Write individual page:
                            if (settings.SAVE_DOWNLOADS_TO_FILE):
                                local_filename = ''.join(["../downloads/pdf/", filename_page])
                                remote_path = ''.join(["transcript/pdf/", filename_page])

                                publish_file(
                                    self.url,
                                    text,
                                    local_filename,
                                    remote_path,
                                    'text/plain'
                                )

                    # Write Entire Text to file
                    if (settings.SAVE_DOWNLOADS_TO_FILE):
                        local_filename = ''.join(["../downloads/pdf/", filename_complete])
                        remote_path = ''.join(["transcript/pdf/", filename_complete])

                        publish_file(
                            self.url,
                            pdf_output,
                            local_filename,
                            remote_path,
                            'text/plain'
                        )

            # takes roughly 90 minutes (16 seconds per page)
            print("The time difference is :",
                  timeit.default_timer() - start_time)

            return pdf_text


        elif (doc_type == 'json'):
            print("SUPPLEMENTAL TEXT()")
            return self.supplemental_text()

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

        elif (doc_type == 'json'):
            print("JSON DOC TYPE")
            text = ''
            if (len(self.media_provider()) > 0):
                text = self.supplemental_text()

            return text

        else:
            return 'error: no doc_type: ' + doc_type

    def content_type_lookup(self):

        if (len(self.content_type) > 0):
            return self.content_type
        else:
            return self.download_resource()['content_type']


    @lru_cache(maxsize=500)
    def doc_type(self):
        # Distinguish between html, text, .doc, ppt, and pdf
        content_type = self.content_type_lookup()
        doc_type = Content_Type.doc_type(content_type)
        return doc_type

    def media_provider(self):

        ext = tldextract.extract(self.url)

        # YouTube
        if (ext.domain == 'youtube' and ext.suffix == 'com'):
            return 'youtube.com'

        elif (ext.domain == 'youtu' and ext.suffix == 'be'):
            return 'youtube.com'

        # Vimeo
        elif (ext.domain == 'vimeo' and ext.suffix == 'com'):
            return 'vimeo.com'

        # Soundcloud
        elif (ext.domain == 'soundcloud' and ext.suffix == 'com'):
            return 'soundcloud.com'

        # OYEZ : Supereme Court Transcripts
        elif (ext.domain == 'oyez' and ext.suffix == 'org'):
            return 'oyez.org'

        # Twitter: TODO
        elif (ext.domain == 'twitter' and ext.suffix == 'com'):
            return 'twitter.com'

        else:
            return ''


    def supplemental_text(self):

        supplemental_text = ''

        media_provider = self.media_provider()

        if (media_provider == 'youtube.com'):
            supplemental_text = YouTubeTranscript(self.url).transcript()

        elif (media_provider == 'vimeo.com'):
            supplemental_text = "Vimeo transcripts not yet implemented. (See document.supplemental_text() )"

        elif (media_provider == 'oyez.org'):
            supplemental_text = OyezTranscript(self.url).transcript()

        elif (media_provider == 'twitter.com'):
            supplemental_text = TwitterTranscript(self.url).transcript()
            # supplemental_text = oyez_transcript(self.url)

        return supplemental_text

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

    @lru_cache(maxsize=500)
    def html(self):
        """ Get html code, if doc_type = 'html' """
        html = ""
        print('unicode' + self.download_resource()['unicode'])

        if self.doc_type() == 'html':
            #html = self.download_resource()['unicode']   #self.raw()
            html = self.unicode

        return html

    @lru_cache(maxsize=20)
    def canonical_url(self):
        """ Web pages may be served from multiple URLs.
            The canonical url is the preferred, permanent URL.
            Use BeautifulSoup to process html and find <link> or <meta> tags.

            Credit: http://pydoc.net/Python/pageinfo/0.40/pageinfo.pageinfo/
        """

        html = self.html()

        return  Canonical_URL(html, url=self.url).canonical_url()

    @lru_cache(maxsize=500)
    def canonical_url_without_protocol(self):
        return url_without_protocol(self.canonical_url())

    @lru_cache(maxsize=500)
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


    @lru_cache(maxsize=500)
    def filename_original(self):
        canonical_path = urllib.parse.quote_plus(self.canonical_url_without_protocol())

        # Example '../downloads/html/avalon.law.yale.edu/19th_century/jeffauto.asp'#
        # original_file_path = '../downloads/' + self.doc_type() + '/' + canonical_path
        original_file_path = '../downloads/' + canonical_path

        return original_file_path

    def filename_text(self):
        return self.canonical_url_without_protocol() + '.txt'


    @lru_cache(maxsize=500)
    def data(self, verbose_view=False):
        """ Dictionary of data associated with URL """
        data = {}
        data['url'] = self.url
        data['canonical_url'] = self.canonical_url()
        data['citeit_url'] = self.citeit_url()
        data['doc_type'] = self.doc_type()
        data['language'] = self.language

        data['encoding'] = self.encoding
        data['request_start'] = self.request_start
        data['request_stop'] = self.request_stop
        data['elapsed_time'] = str(self.elapsed_time())
        data['text'] = self.text()
        data['raw'] = self.raw()

        if (verbose_view):
            data['raw_original_encoding'] = self.raw(convert_to_unicode=False)
            data['num_downloads'] = self.num_downloads

        return data

    def url_encoding_hardcoded(self):
        url_encoding_hardcoded = []
        return url_encoding_hardcoded

    @lru_cache(maxsize=500)
    def encoding_lookup(self):
        """ Returns character-encoding for requested document
        """

        if self.url in self.url_encoding_hardcoded():
            hardcoded_encoding = self.url_encoding_hardcoded()[self.url]
            return hardcoded_encoding

        resource = self.download_resource()
        if resource['encoding']:
            return resource['encoding'].lower()
        else:
            return 'utf-8'  # TODO: Research if this is the proper default

    @lru_cache(maxsize=50)
    def language(self):
        resource = self.download_resource()
        return resource['language']

    @lru_cache(maxsize=50)
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


def format_filename(filename):
    folder_separator = "%2"
    return filename.replace("/", folder_separator)

# Copyright (C) 2015-2018 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.quote_context import QuoteContext
from lib.citeit_quote_context.document import Document
from lib.citeit_quote_context.canonical_url import Canonical_URL
from bs4 import BeautifulSoup
from functools import lru_cache
import hashlib
import time

HASH_ALGORITHM = 'sha256'

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2018 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


class Quote:
    """Looks up quote from cited url and returns the surrounding context

    * Calculates hash of: canonical urls from: citing_url| cited_url|quote
    * Computes text version of html
    * Calculates quote context using: QuoteContext class
        which uses google_diff_match_patch (levenshtein) algorithm
    * Returns: dictionary: data()

    Usage: Quote (
        citing_quote="one does not live by bread alone, "
        "but by every word that comes from the mouth of the Lord",
        citing_url='http://www.citeit.net/demo/',
        cited_url='https://www.biblegateway.com/passage/?search=Deuteronomy+8&amp;version=NRSV'
    )
    """

    def __init__(
        self,
        citing_quote,       # excerpt from citing document
        citing_url,         # url of the document that is doing the quoting
        cited_url,          # url of document that is being quoted
        citing_text='',     # optional: text from citing document
        citing_raw='',      # optional: raw content of citing document
        text_output=True,   # output computed text version of url's html
        raw_output=True,    # output full html/pdf source of cited url
        prior_quote_context_length=500, # length of excerpt before quote
        after_quote_context_length=500, # length of excerpt after quote
        starting_location_guess=None    # guess used by google diff_match_patch
    ):
        self.start_time = time.time()   # measure elapsed time
        self.citing_quote = citing_quote
        self.citing_url = citing_url
        self.cited_url = cited_url
        self.citing_text = citing_text
        self.citing_raw = citing_raw
        self.text_output = text_output
        self.raw_output = raw_output
        self.prior_quote_context_length = prior_quote_context_length
        self.after_quote_context_length = after_quote_context_length
        self.starting_location_guess = starting_location_guess

    ######################## Citing Document ############################
    def citing_url(self):
        return self.citing_url

    @lru_cache(maxsize=20)
    def citing_doc(self):
        """ Get Document of citing url """
        return Document(self.citing_url)

    def citing_raw(self):
        """ Get text-version of citing document """
        citing_raw = self.citing_raw
        if not citing_raw:
            if self.citing_doc():
                citing_raw = citing_doc.raw()
        return citing_raw

    def citing_text(self):
        """ Get text-version of citing document:
            If citing text was passed in to function, use it
            Otherwise look it up using Document class
        """
        citing_text = self.citing_text
        if not citing_text:
            if self.citing_doc():
                citing_text = citing_doc().text()
        return citing_text

    def citing_citeit_url(self):
        """ Check citing page's html (raw) for a canonical url,
            if none found, return the specified url
        """
        html = self.citing_raw
        url = self.citing_url
        citing = Canonical_URL(html, url)
        return citing.citeit_url()

    ########################## Cited Document ##########################
    def cited_url(self):
        return self.cited_url

    @lru_cache(maxsize=20)
    def cited_doc(self):
        """ Get Document of cited url """
        return Document(self.cited_url)

    def cited_raw(self):
        """ Get text-version of citing document """
        cited_raw = ''
        if self.cited_doc():
            cited_raw = cited_doc().raw()
        return cited_raw

    def cited_text(self):
        """ Get text-version of citing document:
            If citing text was passed in to function, use it
            Otherwise look it up using Document class
        """
        cited_text = ''
        if self.cited_doc():
            cited_text = self.cited_doc().text()
        return cited_text

    def cited_citeit_url(self):
        """ Check cited page's html (raw) for a canonical url,
            if none found, return the specified url
        """
        html = self.cited_raw()
        url = self.cited_url()
        cited = Canonical_URL(html, url)
        return cited.citeit_url()

    def hashkey(self):
        """ The hash is based on a concatination of:
            citing_quote|citing_citeit_url|cited_url

            I would like to use the canonical cited_url, but doing so would
            require the authoring software to correct authors when they
            supply a non-canonical url.

            Certain characters (and all spaces) in the citing_quote are removed
            to descrease the liklihood that character irregularites
            throw off the hash
        """

        soup = BeautifulSoup(self.citing_quote, "html.parser")
        citing_quote = soup.get_text()
        replace_text = ['\n', '’', ',', '.' , '-', ':', '/', '!', ' ']
        for txt in replace_text:
            citing_quote = citing_quote.replace(txt, '')
        return ''.join([
                    citing_quote, '|',
                    self.citing_citeit_url(), '|',
                    self.cited_url # future: replace with: self.cited_citeit_url
                ])

    def hash(self):
        """
            Generate hash of the key, based on hash algorith (sha256)
        """
        hash_method = getattr(hashlib, HASH_ALGORITHM)
        hash_text = self.hashkey()
        return hash_method(hash_text.encode('utf-8')).hexdigest()

    def error(self):
        """
            If there is a problem calculating the quote context, an
            error is stored in self.data()['error']
            returns boolean
        """
        return ('error' in self.data())

    def error_str(self):
        return self.data()['error']

    @lru_cache(maxsize=20)
    def data(self, text_output=True, all_fields=True):
        """
            Calculate context of quotation using QuoteContext class
            Optionally return a smaller subset of fields to upload to cloud
        """

        data_dict = {
            'sha256': self.hash(),
            'citing_url': self.citing_url,  #  may be different from canonical
            'cited_url': self.cited_url,    #  may be different from canonical
        }

        # Set text and raw values equal to user-supplied values, or look up
        data_dict['citing_text'] = self.citing_text
        data_dict['cited_text'] = self.cited_text

        if self.raw_output and self.citing_doc():
            data_dict['citing_raw'] = self.citing_raw
            data_dict['cited_raw'] = self.cited_raw

        # Find context of quote from within text
        citing_context = QuoteContext(self.citing_quote, self.citing_text)
        cited_context = QuoteContext(self.citing_quote, self.cited_text())

        # Populate context fields with Document methods
        quote_context_fields = [
            'context_before', 'context_after',
            'quote',
            'quote_start_position', 'quote_end_position',
            'context_start_position', 'context_end_position',
            'quote_length',
            # 'encoding', 'encoding_confidence', 'language'
        ]
        for field in quote_context_fields:
            citing_field = ''.join(['citing_', field])
            cited_field = ''.join(['cited_', field])

            data_dict[citing_field] = citing_context.data()[field]
            data_dict[cited_field] = cited_context.data()[field]

        # Stop Elapsed Timer
        elapsed_time = time.time() - self.start_time
        data_dict['create_elapsed_time'] = format(elapsed_time, '.5f')

        # Don't return certain fields
        if not self.text_output:
            excluded_fields = ['citing_text', 'cited_text']
            for excluded_field in excluded_fields:
                data_dict.pop(excluded_field)

        # Optionally return smaller subset of fields
        if not all_fields:
            excluded_fields = [
                'cited_raw', 'citing_raw',
                'citing_quote_length',
                'cited_quote_start_position', 'citing_quote_start_position',
                'cited_quote_end_position', 'citing_quote_end_position',
                'cited_context_start_position',
                'citing_context_start_position',
                'cited_context_end_position', 'citing_context_end_position',
                'create_elapsed_time',
            ]
            for excluded_field in excluded_fields:
                data_dict.pop(excluded_field, None)

        return data_dict

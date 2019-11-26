# -*- coding: utf-8 -*-

# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.quote import Quote


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2019 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


class QuoteHashTest:

    def __init__(
        self,
        hash_javascript,
        citing_quote,
        citing_url,
        cited_url,
        hashkey_citing

    ):
        self.hash_javascript = hash_javascript
        self.citing_quote = citing_quote
        self.citing_url = citing_url
        self.cited_url = cited_url

    def hash_javascript(self):
        return self.hash_javascript

    def hash_computed(self):
        q = Quote(
            self.hash_javascript,
            self.citing_quote,  # excerpt from citing document
            self.citing_url,    # url of the document that is doing the quoting
            self.cited_url,     # url of document that is being quoted
        )
        return q.hash()

    def hash_match(self):
        return (self.hash_cited()) == (self.hash_citing())

    def hash_citing(self):
        return self.hash_javascript

    def hash_cited(self):
        q = Quote(
            self.citing_quote,  # excerpt from citing document
            self.citing_url,    # url of the document that is doing the quoting
            self.cited_url,     # url of document that is being quoted
        )
        return q.hash()

    def hashkey_cited(self):
        q = Quote(
            self.citing_quote,  # excerpt from citing document
            self.citing_url,    # url of the document that is doing the quoting
            self.cited_url,     # url of document that is being quoted
        )
        return q.hashkey()


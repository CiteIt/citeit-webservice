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
        citing_quote,
        citing_url,
        cited_url,
        hash_javascript,        # 41893361ac4313cfe17df4e6d29e5eb97ef48eb4c3e52ddf561c7a2dff987d7f
        hashkey_javascript      # citingquote|http://citing.com|http://cited.com

    ):
        self.citing_quote = citing_quote
        self.citing_url = citing_url
        self.cited_url = cited_url
        self.hash_javascript = hash_javascript
        self.hashkey_javascript = hashkey_javascript

    def hash_obj(self):
        q = Quote(
            self.citing_quote,  # excerpt from citing document
            self.citing_url,    # url of the document that is doing the quoting
            self.cited_url     # url of document that is being quoted
        )
        return q

    def citing_quote(self):
        return self.citing_quote

    def hash_javascript(self):
        return self.hash_javascript

    def hash_computed(self):
        q = self.hash_obj()
        return q.hash()

    def hash_match(self):
        return (self.hash_computed()) == (self.hash_javascript)

    def hashkey_javascript(self):
        return self.hashkey_javascript()

    def hashkey_computed(self):
        q = self.hash_obj()
        return q.hashkey()

    def hashkey_match(self):
        return self.hashkey_javascript == self.hashkey_computed()

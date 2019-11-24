# -*- coding: utf-8 -*-

# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.tests.quote_hash_match import QuoteHashTest


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2019 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


hash_javascript = "dbff36fd9d7f846834a8ffdf62bdcf4b45a4bace30912c22d1018718a70f8d09"
citing_quote = "<p>Greenspan maximised a form of power that is invaluable to experts. Because journalists admired him, it was dangerous for politicians to pick a fight with the Fed: in any public dispute, the newspaper columnists and talking heads would take Greenspan’s side of the argument. As a result, the long tradition of Fed-bashing ceased almost completely. Every Washington insider understood that Greenspan was too powerful to touch.</p>"
citing_url = "http://demo.citeit.net/index.php/2016/10/22/the-cult-of-the-expert/"
cited_url = "https://www.theguardian.com/business/2016/oct/20/alan-greenspan-cult-of-expert-and-how-it-collapsed"

q = QuoteHashTest(
    hash_javascript,
    citing_quote,   # excerpt from citing document
    citing_url,     # url of the document that is doing the quoting
    cited_url,      # url of document that is being quoted
)
print("URL:       " + q.citing_url)
#print("Quote:     " + q.citing_quote)
print("JS Hash:   " + q.hash_javascript)
print("Computed:  " + str(q.hash_computed()))
print("Match:     " + str(q.hash_match()))
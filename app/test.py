# -*- coding: utf-8 -*-

# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.quote import Quote
from lib.citeit_quote_context.text_convert import TextConvert
from lib.citeit_quote_context.text_convert import html_to_text
import re


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2019 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


hash = "dbff36fd9d7f846834a8ffdf62bdcf4b45a4bace30912c22d1018718a70f8d09"
citing_quote_input = "<p>Greenspan maximised a form of power that is invaluable to experts. Because journalists admired him, it was dangerous for politicians to pick a fight with the Fed: in any public dispute, the newspaper columnists and talking heads would take Greenspan’s side of the argument. As a result, the long tradition of Fed-bashing ceased almost completely. Every Washington insider understood that Greenspan was too powerful to touch.</p>"

citing_url_input = "http://demo.citeit.net/index.php/2016/10/22/the-cult-of-the-expert"

cited_url_input = "https://www.theguardian.com/business/2016/oct/20/alan-greenspan-cult-of-expert-and-how-it-collapsed"


q = Quote(
    citing_quote_input,  # excerpt from citing document
    citing_url_input,  # url of the document that is doing the quoting
    cited_url_input,  # url of document that is being quoted
)
hashkey = q.hashkey()

computed_hash = q.hash()

print("\n\n")
print(hashkey)
print("\n\nHash:         ")
print(hash)
print("\n Computed hash: ")
print(computed_hash)
print("\n\n")
print(hash == computed_hash)
print("\n\n")



"""
quote_text = html_to_text(citing_quote_input)

replace_text = [' ', '\n', 'â€™', ',', '.', '-', '–', '-', '-', '—', ':', '/',
                '!', '`', '~', '^', "’"
    , '&nbsp', '\xa0', '&#8217;'
    , '&#169;', '&copy;', '&#174;'
    , '&reg;', '&#8364;', '&euro;', '&#8482;', '&trade;'
    , '&lsquo;', '&rsquo;', '&sbquo;', '&ldquo;', '&rdquo;', '&bdquo;'
    , '&#34;', '&quot;', '&#38;', '&amp;', '&#39;', '&#163;', '&pound;'
    , '&#165;', '&yen;', '&#168;', '&uml;', '&die;', '&#169;', '&copy;'
    , '\u201c', '“', '”', "‘", "’", '’'
    , '&#8217;', '&#8230;',
                ]

big_regex = re.compile('|'.join(map(re.escape, replace_text)))
the_message = big_regex.sub("", quote_text)


print(the_message)
"""
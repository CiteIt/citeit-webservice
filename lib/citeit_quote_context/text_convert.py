# Copyright (C) 2015-2018 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from bs4 import BeautifulSoup
import re

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2018 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


class TextConvert:

    def __init__(self, str, url=None):
        self.str = str  # page's html, containing potential link, meta tags

    def escape(self):
        txt = self.str

        replace_text = [' ', '\n', 'â€™', ',', '.', '-', ':', '/', '!', '`', '~', '^'
            , '&nbsp', '\xa0', '&#8217;'
            , '&#169;', '&copy;', '&#174;'
            , '&reg;', '&#8364;', '&euro;', '&#8482;', '&trade;'
            , '&lsquo;', '&rsquo;', '&sbquo;', '&ldquo;', '&rdquo;', '&bdquo;'
            , '&#34;', '&quot;', '&#38;', '&amp;', '&#39;', '&#163;', '&pound;'
            , '&#165;', '&yen;', '&#168;', '&uml;', '&die;', '&#169;', '&copy;'
        ]

        for t in replace_text:
            txt = txt.replace(t, '')

        return txt
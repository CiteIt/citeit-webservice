# Copyright (C) 2015-2020 Tim Langeman and contributors
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
__copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = "0.4"


class Canonical_URL:
    """ Find the canonical url within an html document
        Return it if it exists,
        if it does not, return the supplied URL

        USAGE:
            Canonical_URL(
                html = '<html><head><link itemprop="url" rel="canonical" href="http://www.washingtonpost.com/lifestyle/travel/a-national-park-service-photographer-follows-in-the-footsteps-of-ansel-adams/2018/01/12/6da094be-f7b8-11e7-beb6-c8d48830c54d_gallery.html" /></head></html>'
                url = "https://www.washingtonpost.com/lifestyle/travel/a-national-park-service-photographer-follows-in-the-footsteps-of-ansel-adams/2018/01/12/6da094be-f7b8-11e7-beb6-c8d48830c54d_gallery.html?hpid=hp_hp-visual-stories-desktop_no-name%3Ahomepage%2Fstory&utm_term=.6c721cadc76f"
                )
        RETURNS:
            "http://www.washingtonpost.com/lifestyle/travel/a-national-park-service-photographer-follows-in-the-footsteps-of-ansel-adams/2018/01/12/6da094be-f7b8-11e7-beb6-c8d48830c54d_gallery.html"
    """

    def __init__(self, html, url=None):
        self.html = html  # page's html, containing potential link, meta tags
        self.url = url    # optional, default if no canonical value found (or if not an html doc)

    def canonical_url(self):
        """ Web pages may be served from multiple URLs.
            The canonical url is the preferred, permanent URL.
            Use BeautifulSoup to process html and find canonical url
            specified in the <link rel='canonical'> or <meta 'og:url'> tags.

            Credit: http://pydoc.net/Python/pageinfo/0.40/pageinfo.pageinfo/
        """
        canonical_url = ''
        soup = BeautifulSoup(self.html, 'html.parser')

        # (1) Try: <link rel="canonical" href="https://www.example.com/" />
        canonical = soup.find("link", rel="canonical")
        if canonical:
            canonical_url = canonical['href']

        # (2) Try: <meta property="og:url" content="http://example.com">
        else:
            og_url = soup.find("meta", property="og:url")
            if og_url:
                canonical_url = og_url['content']
            else:
                # Assuming not a HTML doc: use the document url
                return self.url

        return canonical_url


    def citeit_url(self):
        """ Use the canonical_url, if it exists.
            Otherwise, use the user-supplied url,
            but chop off the protocol (http://)
        """
        citeit_url = ''
        if self.canonical_url():
            citeit_url = self.canonical_url()

        # (3) If that fails, get the specified url, but chop off the #anchor
        else:
            citeit_url = re.sub(r"/#.*$/", "", self.url)

        # (4) Remove the protocol (http:// or https://)
        return  url_without_protocol(citeit_url.strip())


def url_without_protocol(url):
    """
    Remove: http(s):// and trailing slash
    Before: https://www.example.com/blog/first-post
    After:  www.example.com/blog/first-postj
    """

    url_without_trailing_slash = url.strip("/")

    rec = re.compile(r"https?://")
    url_without_protocol = rec.sub('', url_without_trailing_slash).strip()

    return url_without_protocol
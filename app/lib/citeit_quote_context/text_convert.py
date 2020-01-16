# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
_copyright__ = "Copyright (C) 2015-2019 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


from bs4 import BeautifulSoup
import difflib


class TextConvert:

    def __init__(self, str, url=None):
        self.str = str  # page's html, containing potential link, meta tags

    def escape(self):
        """ Remove the following characters from a string."""

        txt = self.str

        replace_text = [' ', '\n', 'â€™', ',', '.', '-', '–','-','-', '—', ':', '/', '!', '`', '~', '^', "’"
            , chr(34), chr(39), ";"
            , '&nbsp', '\xa0', '&#8217;'
            , '&#169;', '&copy;', '&#174;'
            , '&reg;', '&#8364;', '&euro;', '&#8482;', '&trade;'
            , '&lsquo;', '&rsquo;', '&sbquo;', '&ldquo;', '&rdquo;', '&bdquo;'
            , '&#34;', '&quot;', '&#38;', '&amp;', '&#39;', '&#163;', '&pound;'
            , '&#165;', '&yen;', '&#168;', '&uml;', '&die;', '&#169;', '&copy;'
            , '\u201c', '“', '”', "‘", "’", '’'
            , '&#8217;', '&#8230;',
        ]

        for t in replace_text:
            txt = txt.replace(t, '')

        return txt

def levenshtein_distance(word1, word2):
    """
    https://en.wikipedia.org/wiki/Levenshtein_distance
    :param word1:
    :param word2:
    :return:
    """
    word2 = word2.lower()
    word1 = word1.lower()
    matrix = [[0 for x in range(len(word2) + 1)] for x in range(len(word1) + 1)]

    for x in range(len(word1) + 1):
        matrix[x][0] = x
    for y in range(len(word2) + 1):
        matrix[0][y] = y

    for x in range(1, len(word1) + 1):
        for y in range(1, len(word2) + 1):
            if word1[x - 1] == word2[y - 1]:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,
                    matrix[x - 1][y - 1],
                    matrix[x][y - 1] + 1
                )
            else:
                matrix[x][y] = min(
                    matrix[x - 1][y] + 1,
                    matrix[x - 1][y - 1] + 1,
                    matrix[x][y - 1] + 1
                )

    return matrix[len(word1)][len(word2)]


def show_diff(text, n_text):
    """
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():

        if opcode == 'equal':
            # output.append(seqm.a[a0:a1])
            pass
        elif opcode == 'insert':
            output.append(seqm.b[b0:b1])
        elif opcode == 'delete':
            output.append(seqm.a[a0:a1])
        elif opcode == 'replace':
            output.append(seqm.b[b0:b1])

    return ''.join(output)


def html_to_text(html_str):
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text()

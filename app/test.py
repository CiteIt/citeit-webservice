# -*- coding: utf-8 -*-

# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.tests.quote_hash_match import QuoteHashTest
from lib.citeit_quote_context.url import URL
from lib.citeit_quote_context.text_convert import TextConvert
from lib.citeit_quote_context.text_convert import html_to_text
from lib.citeit_quote_context.text_convert import levenshtein_distance
from lib.citeit_quote_context.text_convert import show_diff

import os
import csv
import requests


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2020 Tim Langeman"
__license__ = "MIT"
__version__ = "0.4"

debug = False

filepath = "test_data/hashkeyTests - version3.csv"
column_names = ['CitingURL', 'Quote', 'CitedURL', 'JavascriptHash', 'JavascriptHashKey']
url_results = {}
extra_chars = set()

file = open(os.path.join(filepath), "r")
reader = csv.DictReader(file, delimiter=',')

for row_num, row in enumerate(reader):

    for column_name in column_names:
        if debug:
            # print(column_name, " : " , row[column_name])
            pass

    if (row_num < 36):
        print("########################################################")

        u = URL(row['CitingURL'])
        citations = u.citations()
        for quote in citations:
            citing_quote = quote['citing_quote']
            citing_quote_original = citing_quote
            citing_quote = html_to_text(citing_quote)
            citing_quote = TextConvert(citing_quote).escape()

        q = QuoteHashTest(
            quote['citing_quote'], # excerpt from citing document
            row['CitingURL'],      # url of the document that is doing the quoting
            row['CitedURL'],       # url of document that is being quoted
            row['JavascriptHash'],
            row['JavascriptHashKey']
        )

        hashkey = citing_quote + "|" + row['CitingURL'] + "|" + row['CitedURL']
        js_hashkey = row['JavascriptHashKey']

        print("URL:    " + str(q.citing_url))
        print("Quote:  " + str(citing_quote_original))
        print("Key:    " + citing_quote)

        if (q.hashkey_diff_length() > 0):
            print("JS:     " + str(q.hashkey_javascript))
            print(">>      " + str(q.hashkey_computed()))
            print("Diff >> " + str(q.hashkey_diff()))


        """
        if debug:
            print("computed: " + str(q.hash_computed()))
            print("js:       " + str(q.hash_javascript))
            print(q.hashkey_computed())

            if q.hashkey_match():
                # print("URL Match: " + str(q.citing_url))
                pass
    
            else:
                print("########################################################")
                print("HASH <>")
                print("URL: " + str(q.citing_url))
                print("Quote:       " + str(q.citing_quote))
    
                print("HASHKEY JS:     : " + str(q.hashkey_javascript))
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print("HASHKEY COMPUTED: " + str(q.hashkey_computed()))
    
                print("JS Hash      :  " + str(q.hash_javascript))
                print("Computed Hash:  " + str(q.hash_computed()))
                print("########################################################")

        url_results[row['CitingURL']] = quote_diff
	"""	

"""
print("\n\n\n")
print("# RESULTS:")

for url, url_quote_diff in url_results.items():
    if len(url_quote_diff) > 0:
        print(str(url_quote_diff), ":", url)


print('Escape these: ' + ''.join(extra_chars))
for char in extra_chars:
    print(char, " : " , ord(char), " : ",  char.encode('utf-8') )
"""

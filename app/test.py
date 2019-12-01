# -*- coding: utf-8 -*-

# Copyright (C) 2015-2019 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.tests.quote_hash_match import QuoteHashTest
import os
import csv


__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2019 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"

debug = True

filepath = "test_data/hashkeyTests - version3.csv"
column_names = ['CitingURL', 'Quote', 'CitedURL', 'JavascriptHash', 'JavascriptHashKey']
url_results = {}

file = open(os.path.join(filepath), "r")
reader = csv.DictReader(file, delimiter=',')

for row_num, row in enumerate(reader):
    #print("########################################################")
    for column_name in column_names:
        if debug:
            # print(column_name, " : " , row[column_name])
            pass

    q = QuoteHashTest(
        row['Quote'],         # excerpt from citing document
        row['CitingURL'],     # url of the document that is doing the quoting
        row['CitedURL'],      # url of document that is being quoted
        row['JavascriptHash'],
        row['JavascriptHashKey']

    )

    if debug:
        print(str(row_num) + "--------------------------------------------------------")

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

    url_results[row['CitingURL']] = q.hashkey_match() # q.hashkey_computed()  #


print("# RESULTS:")
for url, url_match in url_results.items():
    if not url_match:
        print(str(url_match), ":", url)
        pass
     

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

debug = False

filepath = "test_data/hashkeyTests - version3.csv"
column_names = ['CitingURL', 'Quote', 'CitedURL', 'JavascriptHash', 'JavascriptHashKey']
url_results = {}

file = open(os.path.join(filepath), "r")
reader = csv.DictReader(file, delimiter=',')

for row in reader:
    for column_name in column_names:
        if debug:
            print(column_name, " : " , row[column_name])

    q = QuoteHashTest(
        row['JavascriptHash'],
        row['Quote'],   # excerpt from citing document
        row['CitingURL'],     # url of the document that is doing the quoting
        row['CitedURL'],      # url of document that is being quoted
        row['JavascriptHashKey']
    )

    if debug:
        print("URL:         " + str(q.citing_url))
        print("Quote:       " + str(q.citing_quote))

        print("Citing Hash:  " + q.hash_citing())
        print("Cited Hash:   " + str(q.hash_cited()))

    url_results[row['CitingURL']] = q.hash_match()

for url, url_match in url_results.items():
    print(str(url_match), ":", url)
     

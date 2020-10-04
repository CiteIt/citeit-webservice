# -*- coding: utf-8 -*-

# Copyright (C) 2015-2020 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.quote import Quote 

# q = Quote(
# "<p>Be <b>conservative</b> in what you send, be <b>liberal</b> in what you accept</p>",
# "https://192.168.64.2/2017/04/12/was-jesus-a-postel-christian/",
# "https://en.wikipedia.org/wiki/Robustness_principle"
# )

#print(q.hash())

#print(q.hashkey())

from ..lib.citeit_quote_context.document import Document

url = 'https://www.youtube.com/watch?v=Okg2LH6XKzY&feature=youtu.be'

d = Document(url)

text = d.text()

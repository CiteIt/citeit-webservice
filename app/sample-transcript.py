from lib.citeit_quote_context.quote import Quote
from lib.citeit_quote_context.quote_context import QuoteContext
from lib.citeit_quote_context.transcript import YouTubeTranscript

nordstream = Quote (
    "There will be no longer a Nord Stream 2",      # citing_quote
    'https://demo-sites.citeit.net/www.racket.news/p/who-blew-up-the-nord-stream-pipelines/',   # citing_url
    'https://youtube.com/watch?v=qKoPA3M7x2o&feature=shares&t=653'      # cited_url
)

for q in [nordstream]:
    citing_context = QuoteContext(q.citing_quote(), q.citing_text())
    cited_context = QuoteContext(q.citing_quote(), q.cited_text())

text = cited_context.data()['text']
quote = cited_context.data()['quote']
quote_length = len(quote)
start = cited_context.data()['quote_start_position']
after_end = len(text)
end = start + quote_length
lu_quote = text[start:end]
lu_after = text[end:after_end]



"""
cited_context.data['context_start_position'] = context_start_position
cited_context.data['end_position'] = quote_end_position
cited_context.data['context_end_position'] = context_end_position
cited_context.data['context_before'] = context_before
cited_context.data['quote'] = context_quote
cited_context.data['context_after'] = context_after
"""

url = 'https://youtube.com/watch?v=qKoPA3M7x2o&feature=shares&t=653'
yt_no_longer = YouTubeTranscript(url)
transcript_no_longer = yt_no_longer.transcript()
languages = yt_no_longer.languages_available()
default_languages = yt_no_longer.default_language()
yt_text = yt_no_longer.youtube_text()

# qc = QuoteContext(yt_text, quote)

"""
self.quote = normalize_text(quote)
self.text = normalize_text(text)
self.text_output = text_output
self.prior_quote_context_length = prior_quote_context_length
self.after_quote_context_length = after_quote_context_length
"""

print("QUOTE: ")
print(cited_context.data()['quote'])
print("---------------------------------------------------")
print("AFTER: ")
print(cited_context.data()['context_after'])

fields =[
           'quote_length',
           'quote_start_position',
           'quote_end_position',
           'context_start_position',
           'context_end_position',
           'context_after'
]

for field in fields:
    print(field)
    print(cited_context.data()[field])
    print("-----------------------------------------")


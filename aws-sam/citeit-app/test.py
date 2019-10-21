import time

class Quote:
    def __init__(
        self,
        citing_quote_input,     # excerpt from citing document
        citing_url_input,       # url of the document that is doing the quoting
        cited_url_input,        # url of document that is being quote
        citing_text_input='',   # optional: text from citing document
        citing_raw_input='',    # optional: raw content of citing document
        cited_audio_url='',     # optional: audio/podcast URL
        cited_video_url='',     # optional: video url
    ):
        self.start_time = time.time()    # measure elapsed time
        self.citing_quote_input = citing_quote_input
        self.citing_url_input = citing_url_input
        self.cited_url_input = cited_url_input
        self.citing_text_input = citing_text_input
        self.citing_raw_input = citing_raw_input

        self.cited_audio_url = cited_audio_url
        self.cited_video_url = cited_video_url


    def citing_quote(self):
        print(self.citing_quote_input)
        print(self.cited_url_input)


q = {}
q['citing_quote_input'] = 'citing quote'
q['cited_url_input'] = 'cited url input'
q['citing_url_input'] = 'citing url input'
q['citing_text_input'] = 'citing text input'
q['citing_raw_input'] = 'cited raw input'

quote = Quote(**q)
quote.citing_quote()

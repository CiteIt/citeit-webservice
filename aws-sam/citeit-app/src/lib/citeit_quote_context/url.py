# Copyright (C) 2015-2018 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.document import Document
from lib.citeit_quote_context.quote import Quote
from bs4 import BeautifulSoup
from functools import lru_cache
from multiprocessing import Pool
import time

NUM_DOWNLOAD_PROCESSES = 30

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2018 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


class URL:
    """
        Looks up all the citations on a publicly-accessible page
        * Uses Document class to download html source for all documents
        * Uses BeautifulSoup to parse html and locate citations,
          creating a text version of each document
        * Uses Quote and QuoteContext to calculate 500 characters
          before and after citation
        * To Save results, iterate through self.citations() and
          save each quote dictionary

        Custom Data Attributes are used to suppenment <blockquote> and <q> tags:
        Example 1:
          <blockquote
            cite="https://en.wikisource.org/wiki/Pride_and_Prejudice/Chapter_5"
            data-citeit-cited-audio-url="https://en.wikisource.org/wiki/File:Chapter_05_-_Pride_and_Prejudice_-_Jane_Austen.ogg"
            data-citeit-cited-audio-start-time="234"
            data-citeit-cited-title="Pride and Prejudice"
            data-citeit-cited-author="Jane Austen"
            data-citeit-cited-author-wikipedia-url="https://en.wikipedia.org/wiki/Jane_Austen"
            data-citeit-cited-work-wikipedia-url="https://en.wikipedia.org/wiki/Pride_and_Prejudice"
          >I could easily forgive his pride, if he had not mortified mine.</blockquote>

        Example 2:
          <blockquote
            cite="https://medium.com/conversations-with-tyler/rabbi-david-wolpe-leaders-religion-israel-identity-7c159c2ed2d"
            data-citeit-cited-audio-url="https://soundcloud.com/conversationswithtyler/rabbi-david-wolpe-on-leadership-religion"
            data-citeit-cited-video-url="https://youtu.be/DH0VqlPnzpE"
            data-citeit-transcript-url="https://medium.com/conversations-with-tyler/rabbi-david-wolpe-leaders-religion-israel-identity-7c159c2ed2d"
            data-citeit-cited-audio-start-time="2751"
            data-citeit-cited-video-start-time="2751"
            data-citeit-cited-title="Rabbi David Wolpe on Leadership, Religion, and Identity (Ep. 19 — Live at Sixth & I)"
            data-citeit-cited-series="Conversations with Tyler"
            data-citeit-cited-series-url="https://conversationswithtyler.com"
            data-citeit-cited-series-youtube="https://www.youtube.com/playlist?list=PLS8aEHTqDvpInY9kslUOOK8Qj_-B91o_W"
            data-citeit-cited-authors_names="David Wolpe, Tyler Cowen"
            data-citeit-cited-authors_twitter="@RabbiWolpe, @tylercowen"
            data-citeit-cited-authors-wikipedia-urls="https://en.wikipedia.org/wiki/David_Wolpe, https://en.wikipedia.org/wiki/Tyler_Cowen "
          >I think that Judaism has the same problem that any thick civilization has in a world in which,
          as you say, context is stripped away. And not only is context stripped away,
          but attention to any one thing is scanter and less than it used to be. So, for example,
          a lot of Jewish commentary is based on your recognizing the reference that I make.
          Who recognizes references anymore? Because people don’t spend years studying books.</blockquote>


        Example 3:
        <blockquote
            cite="https://apps.oyez.org/player/#/roberts2/oral_argument_audio/22476"
            data-citeit-cited_audio_url='https://s3.amazonaws.com/oyez.case-media.ogg/case_data/2008/08-205/20090909r_08-205.ogg',
            data-citeit-cited_audio_start_time='3433',
            data-citeit-cited_transcript_url='https://apps.oyez.org/player/#/roberts2/oral_argument_audio/22476',
            data-citeit-citing_tags='supreme-court, supreme-court-citizens-united, justice-kennedy',
            data-citeit-cited_title='Case 08-205, Citizens United v. The Federal Election Commission',
            data-citeit-cited_authors_names='Anthony Kennedy',
            data-citeit-cited_authors_urls='https://supremecourthistory.org/history-of-the-court/the-current-court/justice-anthony-kennedy/, https://www.oyez.org/justices/anthony_m_kennedy',
            data-citeit-cited_authors_twitter='https://twitter.com/hashtag/justice%20kennedy',
            data-citeit-cited_authors-wikipedia-urls = 'https://en.wikipedia.org/wiki/Anthony_Kennedy'
            data-citeit-cited_author_wikipedia_url= 'https://en.wikipedia.org/wiki/Supreme_Court_of_the_United_States',
            data-citeit-cited_authors_entities='https://twitter.com/hashtag/justice%20kennedy',
            data-citeit-cited_authors_entities_urls = "https://www.supremecourt.gov/"
            data-citeit-citeit_cited_work_wikipedia_url="https://en.wikipedia.org/wiki/Citizens_United_v._FEC"
            data-citeit-cited_series = 'Oyez Supreme Court Resources',
            data-citeit-cited_eries_url = 'https://www.oyez.org/',
            data-citeit-cited_event_date='2009-09-09',
            data-citeit-cited_event_location='United States Supreme Court, Washington, D.C (USA)',
            data-citeit-cited_event_lattitue='38.890556',
            data-citeit-cited_event_longitude='77.004444',
        >The government silences a corporate objector, and those corporations may have the most knowledge of this on the subject.
        Corporations have lots of knowledge about environment, transportation issues, and you are silencing them during the election.
        </blockquote>

        Example 4:
        <blockquote
            cite="https://gimletmedia.com/shows/reply-all/o2hx34/127-the-crime-machine-part-i"
            data-citeit-cited_audio_url='https://dcs.megaphone.fm/GLT1353849859.mp3?key=9ee13f8c1681e531a9a098bdad57b7f8',
            data-citeit-cited_audio_start_time='',
            data-citeit-cited_transcript_url='https://gimletmedia.com/shows/reply-all/o2hx34/127-the-crime-machine-part-i',
            data-citeit-citing_tags='reply-all-podcast, police, crime, crime-history, new-york-city, comsats, jack-maple',
            data-citeit-cited_title='The Crime Machine, Part I, Episode 127',
            data-citeit-cited_authors_names='PJ Vogt, ',
            data-citeit-cited_authors_twitter='@PJVogt',
            data-citeit-cited_authors_entities='Reply-All',
            data-citeit-cited_authors_entities_urls = "https://en.wikipedia.org/wiki/Reply_All_(podcast)",
            data-citeit-cited_series = 'Reply-All',
            data-citeit-cited-series-url="https://gimletmedia.com/shows/reply-all/episodes",
            data-citeit-cited-series-youtube="https://www.youtube.com/playlist?list=PLS8aEHTqDvpInY9kslUOOK8Qj_-B91o_W",
            data-citeit-cited_event_date='2018-10-12'
        >J: The thing that was weird about the job was that Pedro's bosses didn't really seem to want him to pursue the actual, violent, serious crimes that he saw. What they wanted him to do instead was just to write summonses. Summonses are just the tickets that cops give out for the low-level stuff, misdemeanors. You'd give a summons to a guy drinking a beer in the street or riding his bike on the sidewalk. There was a lot of pressure to write summonses.

PEDRO: One of the ones that, you know, never leave my head was it was overtime. We’re ordered to write five. And the van–

PJ: Write five like you had to–you have overtime but you gotta come back with five summons?

PEDRO: Five summonses or get dealt with. I’ll explain that later. Well, we, uh, we’re driving around and the senior guy stops and says, “All right. This is one.”

PJ: It's really early in the morning. The streets are almost completely empty. It's hard to even find a person, let alone somebody doing something wrong. Their boss is pointing at this man who’s just standing on the sidewalk alone, outside a store. But the van stops.

PEDRO: Some guy jumps out. And this one guy, in front of a bodega, doing absolutely nothing, they gave him a summons for blocking pedestrian traffic. You know, we were just shaking our heads like, “What did you give him?” “Blocking pedestrian traffic.” And they just start laughing. I'm like, oh wow. All right. So we move on.

PJ: Pedro says the next stop was this Mexican man who was just sitting alone on a stoop. They wrote him up for the exact same thing: Blocking pedestrian traffic.

PEDRO: And this was all night until all of us–there was like a four or five of us in the van, until everyone had five.

PJ: Pedro was so confused by what had had happened that night, he actually went home, and looked up the definition of blocking pedestrian traffic. These guys had not been blocking pedestrian traffic. This was absurd. And Pedro didn't know it, but all over the city cops were getting pushed in the exact same way -- to aggressively write summonses to people for doing seemingly nothing. I talked to another cop, this guy in Brooklyn named Edwin Raymond.

EDWIN RAYMOND: After the academy, I would run into officers that I was in the academy with. And it’d be like, “Oh, hey, what's up? Are you still at transit?” And the third question, without fail, the third question was always, “What do they want from you guys over there?” That’s how much this is part of the culture.</blockquote>



    """
    # Use Custom Data Attributes prefix:
    # http://html5doctor.com/html5-custom-data-attributes/
    data_attr_prefix = "data-citeit-"


    def __init__(self, url):
        self.start_time = time.time()  # measure elapsed execution time
        self.url = url   # user-supplied url

        # get text version of citing page to passed it into load_quote_data()
        self.text = self.text()

    def __str__(self):
        return self.url

    @property
    def base_fields(self):
        return = [
            'citing_quote',
            'citing_url',
            'citing_text',
            'citing_raw',
            'cited_url',
        ]

    @property
    def attr_fields(self):

        return = [
            'cited_audio_url',
            'cited-audio-start-time',
            'cited_video_url',
            'cited-video-start-time',
            'cited_transcript_url',
            'citing_tags',
            'cited_microformat_url',
            'cited_title',
            'cited_author_entity',
            'cited_authors_names',
            'cited_authors_urls',
            'cited-authors_twitter',
            'cited-authors-wikipedia-urls',
            'cited-work-wikipedia-url',
            'cited-series',
            'cited-series-url',
            'cited-series-youtube',
            'cited_event_date',
            'cited_event_location',
            'cited_event_lattitue',
            'cited_event_longitude'
        ]

    # Document methods imported here so class can make only 1 request per URL
    @lru_cache(maxsize=50)
    def doc(self):
        """ Call Document class """
        return Document(self.url)

    def raw(self):
        """ Return raw data of requested document """
        return self.doc().raw()

    # @lru_cache(maxsize=50)
    def text(self):
        """ Return text version of requested document """
        return self.doc().text()

    def html(self):
        """ If doc_type = 'html', return raw document """
        html = ''
        if (self.doc_type() == 'html'):
            html = self.raw()
        return html

    def doc_type(self):
        """ The class only supports 'html' document types now,
            but could expand to include pdf, word docs and text
        """
        return 'html'  # hard-coded.  Todo: pdf, doc, docx, text

    def citation_all_fields(self):
        return self.base_fields() + self.attr_fields()

    @lru_cache(maxsize=20)
    def citation_attributes(self):
        """ Returns a dictionary of:
                url and
                quote text
            from all blockquote and q tags on this page
        """
        print("Getting URLs ..")


        url_attr = {}
        link_attr = {}
        citation_attrs = []
        for field in self.citation_all_fields():
          citation_attr[data_attr_prefix + field]

        soup = BeautifulSoup(self.html(), 'html.parser')
        for citation in soup.find_all(['blockquote', 'q']):
          if citation.get('cite'):
            # Get Pairing: URL & Quotation Text
            link_attr['text'] = citation.text

            # Some citations have extra attributes: data-citeit-cited-audio-url
            for citation_attr in citation_attrs:
              if citation.has_attr(citation_attr):
                attr_key = citation_attr.replace(
                    data_attr_prefix, "", citation_attr
                )
                link_attr[attr_key] = citation.get[citation_attr]
            url_attr[cite.get('cite')] = link_attr
        return url_attr

    def citation_url_text(self):
        """ Simplify dictionary to return only URL and text

             Returns a dictionary of:
                url and
                quote text
            from all blockquote and q tags on this page
        """

        url_text = {}
        for url, attr in self.citation_attributes():
            url_text[url] = attr['text']
        return url_text

    def citation_urls(self):
        """ Returns a list of the urls that have been cited """
        urls = []
        for url, text in self.citation_url_text().items():
            urls.append(url)
        return urls

    def citations_list_dict(self):
        """ Create list of quote dictionaries
            to be passed to map function.  Data is supplied
            from urls and text specified in citing
            document's blockquote and 'cite' attribute."""

        quote = {}
        citations_list_dict = []
        for cited_url, citing_attr in self.citation_url_text().items():
            for key in self.base_fields():
                quote[key] = citing_attr[key]

            for key in self.attr_fields():
                quote[key] = citing_attr['data-citeit' + key]

            citations_list_dict.append(quote)
        return citations_list_dict

    def citations(self):
        """ Return a list of Quote Lookup results for all citations on this page
            Uses asychronous pool to achieve parallel processing
            calls load_quote_data() function
            for all values in self.citations_list_dict
            using python 'map' function
        """
        result_list = []
        citations_list_dict = self.citations_list_dict()
        pool = Pool(processes=NUM_DOWNLOAD_PROCESSES)

        # try:
        result_list = pool.map(load_quote_data, citations_list_dict)

        # except ValueError:
        #    # TODO: add better error handling
        #    print("Skipping map value ..")
        pool.close()
        pool.join()
        return result_list


# ################## Non-class functions #######################


def load_quote_data(quote_keys):
    """ lookup quote data, from keys """
    print("Downloading citation for: " + quote_keys['citing_quote'])
    quote = Quote(**quote_keys)
    return quote.data()
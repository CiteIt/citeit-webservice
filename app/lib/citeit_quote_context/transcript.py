# Copyright (C) 2015-2022 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.misc.utils import get_from_cache
from lib.citeit_quote_context.misc.utils import publish_file

import tweepy
import youtube_dl
import settings

import tldextract
import requests
import itertools
import operator
import re
import os

from urllib.parse import urlparse
from functools import lru_cache


__author__ = 'Tim Langeman'
__email__ = 'timlangeman@gmail.com'
__copyright__ = 'Copyright (C) 2015-2022 Tim Langeman'
__license__ = 'MIT'
__version__ = '0.4'



class YouTubeTranscript:
    """
        Check to see if transcript was already downloaded and cached
        If not, query the YouTube API and parse the response into a transcript
            - get RAW transcript with time codes
            - remove formatting and time codes

        USAGE:
            from lib.citeit_quote_context.transcript import YouTubeTranscript
            url = 'https://youtu.be/GOnpVQnv5Cw'
            t = YouTubeTranscript(url)
            t.transcript('')
    """

    def __init__(
        self,
        url, 
        line_separator='', 
        timesplits=''
    ):
        self.url = url
        self.line_separator = line_separator
        self.timesplits = timesplits

    def transcript(self, line_separator='\n\n', cache=True):

        # is a cached version available?
        if cache and (len(self.transcript_cache()) > 0):
            return self.transcript_cache()

        return self.youtube_text(line_separator)


    def publish(self):

        if settings.SAVE_DOWNLOADS_TO_FILE:
            print('create/write file: ' + self.transcript_filename())
          
            local_filename = '../transcripts/' + self.youtube_video_id() + '.txt'
            remote_path = ''.join(['transcript/custom/youtube.com/', self.youtube_video_id() , '.txt'])

            publish_file(
                self.url,
                self.transcript(),
                local_filename,
                remote_path,
                'text/plain'
            )

    def transcript_filename(self):
        return '../downloads/transcripts/custom/youtube.com/' + self.youtube_video_id() + '.txt'

    def transcript_cache(self):
        """
            Get cached version fo transcript
        """

        file_dict = get_from_cache(self.transcript_filename())
        transcript_content = file_dict['text']

        return transcript_content or ''


    def youtube_video_id(self):
        # Get id from YouTube URL
        # Credit: https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python

        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        
        query = urlparse(self.url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail?
        return None


    def youtube_raw(self):
        """
            Download YouTube Transcript from API
            RAW Transcript which includes time signatures and WEBVTT
        """
            
        try:
            ydl = youtube_dl.YoutubeDL(
                {'writesubtitles': True,
                'allsubtitles': True,
                'writeautomaticsub': True
                }
            )
            res = ydl.extract_info(self.url, download=False)

        except youtube_dl.utils.DownloadError:
            return 'ERROR: YouTube said: Unable to extract video data'
        
        return res

    def youtube_text(self, line_separator = ''):

        transcript_output = []
        res = self.youtube_raw()

        # Remove lines that contain the following phrases
        remove_words = [
                        '-->'               #   Usage: 00:00:01.819 --> 00:00:01.829
                        , 'Language: en'
                        , ': captions'
                        , 'WEBVTT'
                        , '<c>'
                    ]

        if res['requested_subtitles'] and res['requested_subtitles']['en']:

            print('Grabbing vtt file from ' +
                res['requested_subtitles']['en']['url']
            )
            response = requests.get(
                res['requested_subtitles']['en']['url'],
                stream=True
            )

            text = response.text

            # Remove Formatting: time & color ccodes
            # Credit: Alex Chan
            # Source: https://github.com/alexwlchan/junkdrawer/blob/d8ee4dee1b89181d114500b6e2d69a48e2a0e9c1/services/youtube/vtt2txt.py

            # Throw away the header, which is of the form:
            #
            #     WEBVTT
            #     Kind: captions
            #     Language: en
            #     Style:
            #     ::cue(c.colorCCCCCC) { color: rgb(204,204,204);
            #      }
            #     ::cue(c.colorE5E5E5) { color: rgb(229,229,229);
            #      }
            #     ##
            #

            #>>>>>>>>>>>text = text.split("##\n", 1)[1]

            # Now throw away all the timestamps, which are typically of
            # the form:
            #
            #     00:00:01.819 --> 00:00:01.829 align:start position:0%
            #
            text, _ = re.subn(
                r'\d{2}:\d{2}:\d{2}\.\d{3} \-\-> \d{2}:\d{2}:\d{2}\.\d{3} align:start position:0%\n',
                '',
                text
            )

            # And the color changes, e.g.
            #
            #     <c.colorE5E5E5>
            #

            ###### text, _ = re.subn(r'<c\.color[0-9A-Z]{6}>', '', text)

            # And any other timestamps, typically something like:
            #
            #    </c><00:00:00,539><c>
            #
            # with optional closing/opening tags.
            #######text, _ = re.subn(r'(?:</c>)?(?:<\d{2}:\d{2}:\d{2}\.\d{3}>)?(?:<c>)?',
            #######                  '', text)

            # 00:00:03,500 --> 00:00:03,510
            text, _ = re.subn(
                r'\d{2}:\d{2}:\d{2}\.\d{3} \-\-> \d{2}:\d{2}:\d{2}\.\d{3}\n', '',
                text)

            # Now get the distinct lines.
            text = [line.strip() + ' ' for line in text.splitlines() if line.strip()]

            # Credit: Hernan Pesantez: https://superuser.com/users/1162906/hernan-pesantez
            # https://superuser.com/questions/927523/how-to-download-only-subtitles-of-videos-using-youtube-dl

            for line, _ in itertools.groupby(text):
                if not any(remove_word in line for remove_word in remove_words):
                    line = line.replace('&gt;', '')
                    line = line.replace('   ', ' ')
                    line = line.replace('  ', ' ')
                    try:
                        line = line.strip() + ' ' + line_separator
                    except:
                        line = line.strip() + ' ' + str(line_separator)

                    transcript_output.append(line)

            if len(res['subtitles']) > 0:
                print('manual captions')
            else:
                print('automatic_captions')

        else:
            print('Youtube Video does not have any english captions')
        
        return ''.join(transcript_output)


class OyezTranscript:
    """
        Check to see if transcript was already downloaded and cached
        If not, query the Oyez API and parse the response into a transcript

        USAGE:
            from lib.citeit_quote_context.transcript import OyezTranscript
            url = 'https://api.oyez.org/case_media/oral_argument_audio/22476'
            t = OyezTranscript(url)
            t.transcript(' ')
    """

    def __init__(
        self,
        url,
        line_separator = '', 
        timesplits = ''
    ):
        self.url = str(url)  # also allow transcript_id to be entered as an Int
        self.line_separator = line_separator
        self.timesplits = timesplits
    
    def transcript_id(self):
        return re.match('.*?([0-9]+)$', self.url).group(1)

    def json_url(self):
        return 'https://api.oyez.org/case_media/oral_argument_audio/' + self.transcript_id()

    def transcript_filename(self):
        return '../downloads/transcripts/custom/oyez.org/' + self.transcript_id() + '.txt'

    def transcript_cache(self):
        # Get cached version of transcript
        file_dict = get_from_cache(self.transcript_filename())
        transcript_content = file_dict['text']
        return transcript_content or ''

    def transcript(self, line_separator='\n\n', cache=True):
        """
            Extract transcript from JSON data
            Example: https://api.oyez.org/case_media/oral_argument_audio/22476
        """

        transcript_content = self.transcript_cache()

        # is a cached version available?
        if cache and (len(self.transcript_cache()) > 0):
            return transcript_content

        # Convert public json url to text transcript
        if (len(self.json_url()) == 0):
            print("NOT: " + self.json_url())
            return ''
        else:
            print("OYEZ JSON: " + self.json_url())

            output = ''
            line_output = ''

            print(self.json_url())

            r = requests.get(url=self.json_url())
            data = r.json()  # Check the JSON Response Content documentation below

            for sections in data['transcript']['sections']:

                for turns in sections['turns']:
                    turn_num = 0

                    for section_dict in turns:
                        section_num = 0

                        for text in turns['text_blocks']:
                            if (text['text'] != line_output):

                                if (turn_num == 0):
                                    output = output + text['text'] + line_separator
                                line_output = text['text']

                            section_num = section_num + 1

                        turn_num = turn_num + 1

            return output

    def publish(self):
        
        if settings.SAVE_DOWNLOADS_TO_FILE:
            print('create/write file: ' + self.transcript_filename())
          
            local_filename = '../transcripts/oyez.org/' + self.transcript_id() + '.txt'
            remote_path = ''.join(['transcript/custom/oyez.org/', self.transcript_id() , '.txt'])

            publish_file(
                self.url,
                self.transcript(),
                local_filename,
                remote_path,
                'text/plain'
            )


class TwitterTranscript:
    """
        Check to see if transcript was already downloaded and cached
        If not, query the Oyez API and parse the response into a transcript

        USAGE:
            from lib.citeit_quote_context.transcript import OyezTranscript
            url = 'https://twitter.com/NewsHour/status/1375707662197919746'
            t = TwitterTranscript(url)
            t.transcript(' ')
    """

    def __init__(
        self,
        url,
        line_separator = '' 
    ):
        self.url = url
        self.line_separator = line_separator

        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth)

    def id(self):
        id_matches = re.findall(r'\d+', self.url)

        if len(id_matches) > 0:
            return id_matches[0]  # first matching digits
        else:
            return -1   # not found
        
    def transcript(self, line_separator='\n\n', cache=True):

        t = self.api.get_status(self.id(), tweet_mode="extended")
        return t.full_text

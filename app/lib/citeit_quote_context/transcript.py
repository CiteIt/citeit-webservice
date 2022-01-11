# Copyright (C) 2015-2022 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

from lib.citeit_quote_context.misc.utils import get_from_cache
from lib.citeit_quote_context.misc.utils import publish_file

import youtube_dl
import settings

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

    def transcript(self, cache=True):

        # is a cached version available?
        if cache and (len(self.transcript_cache()) > 0):
            return self.transcript_cache()

        # lookup and deduplicate results    
        return self.youtube_deduplicated()


    def publish_transcript(self):

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
        transcript_content = ''

        file_dict = get_from_cache(self.transcript_filename())
        transcript_content = file_dict['text']

        return transcript_content


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

    def youtube_text(self):

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
                        line = line.strip() + ' ' + self.line_separator
                    except:
                        line = line.strip() + ' ' + str(self.line_separator)

                    transcript_output.append(line)

            if len(res['subtitles']) > 0:
                print('manual captions')
            else:
                print('automatic_captions')

        else:
            print('Youtube Video does not have any english captions')
        
        return ''.join(transcript_output)

    def youtube_deduplicated(self):

        transcript_content = ''
        transcript_output = []
        deduplicated_output = ''
        duplicate_cnt = 0
        content_file = ''

        transcript_output = self.youtube_text()

        # Check to see if lines are duplicated
        line_counter = {}
        counter_cnt = {}
        deduplicated_output = []

        # Count each line
        for line in transcript_output:

            if (line not in line_counter):
                line_counter[line] = 1
            else:
                current_cnt = line_counter[line]
                line_counter[line] = current_cnt + 1

        # How many lines have each count?
        for line, cnt in line_counter.items():

            if cnt not in counter_cnt:
                counter_cnt[cnt] = 1
            else:
                counter_cnt[cnt] = counter_cnt[cnt] + 1

        # Are lines being duplicated or triplicated at higher frequency that single lines?
        if (any(counter_cnt.values())):  # not empty
            max_count = max(counter_cnt.items(), key=operator.itemgetter(1))[0]
        else:
            max_count = 0

        # Regular Line Count
        if (max_count == 1):
            transcript_output =  ''.join(transcript_output)

        # Duplicate Lines Found
        else:
            print('De-duplicate transcripts:', max_count)
            for line_num, line in enumerate(transcript_output):
                if (line_num%max_count) == 1:  # Get every n lines
                    deduplicated_output.append(line)

            transcript_output = ''.join(deduplicated_output)

        # Combine lines
        transcript_output = ''.join(transcript_output)

        # Replace Special characters
        transcript_output = transcript_output.replace('   ', ' ')
        transcript_output = transcript_output.replace('  ', ' ')
        transcript_output = transcript_output.replace('WEBVTT Kind', ' ')
        transcript_output = transcript_output.replace('WEBVTTKind', ' ')
        transcript_output = transcript_output.strip()

        return transcript_output

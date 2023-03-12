# Purpose: Get video transcript with timestamps for YouTube video
# Source:  https://github.com/CiteIt/citeit-webservice/blob/master/app/lib/citeit_quote_context/trump-rally-transcript.py

# Command: python3 trump-rally-transcript.py

# Requires installing 
#    yt_dlp: https://pypi.org/project/yt_dlp/
#    requests:   https://pypi.org/project/requests/

import itertools
import operator
import re
import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib.parse import urlparse

from pathlib import Path

import urllib
from urllib.parse import urlparse
from urllib.parse import parse_qs

import re
import yt_dlp


url = 'https://youtu.be/ht20eDYmLXU'  # Trump Rally
line_separator = ''

transcript_content = ''
transcript_output = []
deduplicated_output = ''
duplicate_cnt = 0
content_file = ""


# Download YouTube Transcript from API
ydl = yt_dlp.YoutubeDL(
    {'writesubtitles': True,
        'allsubtitles': True,
        'writeautomaticsub': True
    }
)
res = ydl.extract_info(url, download=False)

# Remove lines that contain the following phrases
remove_words = [
                "-->"               #   Usage: 00:00:01.819 --> 00:00:01.829
                , "Language: en"
                , ": captions"
                , "WEBVTT"
                , "<c>"
            ]

if res['requested_subtitles'] and res['requested_subtitles'][
    'en']:
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
    text = [line.strip() + " " for line in text.splitlines() if line.strip()]

    # Credit: Hernan Pesantez: https://superuser.com/users/1162906/hernan-pesantez
    # https://superuser.com/questions/927523/how-to-download-only-subtitles-of-videos-using-youtube-dl

    for line, _ in itertools.groupby(text):
        if not any(remove_word in line for remove_word in remove_words):
            line = line.replace("&gt;", "")
            line = line.replace("   ", " ")
            line = line.replace("  ", " ")
            line = line.strip() + " " + line_separator

            transcript_output.append(line)

    if len(res['subtitles']) > 0:
        print('manual captions')
    else:
        print('automatic_captions')

else:
    print('Youtube Video does not have any english captions')


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
    transcript_output =  "".join(transcript_output)

# Duplicate Lines Found
else:
    print("De-duplicate transcripts:", max_count)
    for line_num, line in enumerate(transcript_output):
        if (line_num%max_count) == 1:  # Get every n lines
            deduplicated_output.append(line)

    transcript_output = "".join(deduplicated_output)


# Combine lines
transcript_output = "".join(transcript_output)

# Replace Special charachters
transcript_output = transcript_output.replace("   ", " ")
transcript_output = transcript_output.replace("  ", " ")
transcript_output = transcript_output.replace("WEBVTT Kind", " ")
transcript_output = transcript_output.replace("WEBVTTKind", " ")
transcript_output = transcript_output.strip()

print(transcript_output)
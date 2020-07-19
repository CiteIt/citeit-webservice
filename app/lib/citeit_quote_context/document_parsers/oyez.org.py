import requests
import re

def get_domain(public_url):
    from urllib.parse import urlparse
    parsed_uri = urlparse(public_url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain

def oyez_public_json(public_apps_url):
    # Lookup case_id from apps url and return api url
    print("URL: " + public_apps_url)
    json_url = ''

    if (get_domain(public_apps_url) == 'apps.oyez.org'):
        case_id = re.match('.*?([0-9]+)$', public_apps_url).group(1)
        json_url = 'https://api.oyez.org/case_media/oral_argument_audio/' + case_id

    else:
        print("NOT: app.oyeze.org")

    return json_url


def oyez_transcript(public_url):
    # Convert public json url to text transcript

    json_url = oyez_public_json(public_url)
    print("JSON: " + json_url)

    if (len(json_url) == 0):
        print("NOT: " + json_url)
        return ''

    else:
        output = ''
        line_output = ''

        r = requests.get(url=json_url)
        data = r.json()  # Check the JSON Response Content documentation below

        for num, sections in enumerate(data['transcript']['sections']):

            for turns in sections['turns']:
                turn_num = 0

                for section_dict in turns:
                    section_num = 0

                    for text in turns['text_blocks']:
                        if (text['text'] != line_output):

                            if (turn_num == 0):
                                output = output + text['text'] + "\n\n"
                            line_output = text['text']

                        section_num = section_num + 1

                    turn_num = turn_num + 1

        return output

#-------------------------------- Main --------------------------------#

public_url = "https://apps.oyez.org/player/#/roberts2/oral_argument_audio/22476"
domain = get_domain(public_url)
transcritpt_text = ''

# Oyez: Supreme Court Hearings (transcripts)
if (domain == 'apps.oyez.org'):
    transcritpt_text = oyez_transcript("https://apps.oyez.org/player/#/roberts2/oral_argument_audio/22476")

print(transcritpt_text)
from bs4 import BeautifulSoup
from urllib.parse import urlparse, ParseResult
import ftfy  # fix bad unicode
import boto3
import settings
import gzip
import os
import re

from langdetect import detect


def escape_json(str):
    # str = str.replace('&apos', '&apos;')

    # soup = BeautifulSoup(str)
    return str #soup.text


def save_citation(json_quote):

    """
    insert/update citation set
        cited_context_after
        cited_context_before
        cited_quote
        cited_url
        citing_context_after
        citing_quote
        citing_url
        hashkey
        sha256
    """



def fix_url(url):
    # Credit: https://stackoverflow.com/questions/21659044/how-can-i-prepend-http-to-a-url-if-it-doesnt-begin-with-http
    # JBernardo: https://stackoverflow.com/users/754991/jbernardo

    p = urlparse(url, 'http')
    netloc = p.netloc or p.path

    path = p.path if p.netloc else ''
    if not netloc.startswith('www.'):
        netloc = 'www.' + netloc

    p = ParseResult('http', netloc, path, *p[3:])
    return p.geturl()


def fix_encoding(str):
    # If certain characters are found in the input, switch encoding
    output = str

    output = ftfy.fix_text(str)
    return output

def convert_quotes_to_straight(str):
    """ TODO: I'm cutting corners on typography until I figure out how to
        standardize curly and straight quotes better.

        The problem I'm trying to solve is that a quote may use a different
        style of quote or apostrophe symbol than its source,
        but I still want the quotes match it, so I'm converting
        all quotes and apostrophes to the straight style.
    """
    if str:  # check to see if str isn't empty
        str = str.replace("”", '"')
        str = str.replace("“", '"')
        str = str.replace("’", "'")

        str = str.replace('&#39;', "'")
        str = str.replace('&apos;', "'")
        str = str.replace(u'\xa0', u' ')
        str = str.replace('&\rsquo;', "'")
        str = str.replace('&lsquo;', "'")

        str = str.replace('&rsquo;', '"')
        str = str.replace('&lsquo;', '"')
        str = str.replace("\201C", '"')
        str = str.replace(u"\u201c", "")
        str = str.replace(u"\u201d", "")
    return str

def normalize_whitespace(str):
    """
        Convert multiple spaces and space characters to a single space.
        Trim space at the beginning and end of the string
    """
    if str:  # check to see if str isn't empty
        str = str.replace("&nbsp;", " ")
        str = str.replace(u'\xa0', u' ')
        str = str.strip()               # trim whitespace at beginning and end
        str = re.sub(r'\s+', ' ', str)  # convert multiple spaces into single space
    return str


def format_filename(filename):
    folder_separator = "%2"
    return filename.replace("/", folder_separator)


def publish_file(url, text, local_path, remote_path, content_type, compression=''):

    string_input = text
    local_path_input = local_path

    filename, file_extension = os.path.splitext(local_path)

    if (file_extension == '.txt'):
        content_type = 'text/plain'

    elif (file_extension == 'json'):
        content_type = 'application/json'

    elif (file_extension == 'html'):
        content_type = 'text/html'

    elif (file_extension == 'html'):
        content_type = 'application/pdf'


    filetype = 'wb'

    if compression:
        # content_type = 'application / x - gzip'
        # To decompress: string_input = gzip.decompress(string_input)

        # local_path_input = local_path + '.gz'
        # string_input = gzip.compress(bytes(text, 'utf-8'))
        pass

    print("Input path: >> " + local_path_input )
    print("Compression: " + compression)

    save_file_locally(local_path_input, string_input, filetype)
    save_file_to_cloud(local_path_input, remote_path, content_type, compression)
    print("SAVED TO CLOUD:  ------------" + remote_path + "---------------")
    submit_to_archive_org(url)

def save_file_locally(local_path, text_input, filetype='w'):
    # Create Local Directory if it doesn't exist

    dirname = os.path.dirname(local_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Archive file
    print("SAVE LOCALLY: local filename----------------------------------")
    print(local_path)
    with open(local_path, 'w') as f:
        f.write(text_input)

    print("**** Saved locally: " + local_path + " ******")


def save_file_to_cloud(local_path, remote_path, content_type, compression='gzip'):

    if (local_path != '../downloads/'):

        extraArgs = {   'ContentType': content_type,
                        'ACL': "public-read"
                    }

        if (compression == 'gzip'):
            extraArgs['ContentEncoding'] = compression

        remote_path = remote_path.replace('https://', '')
        remote_path = remote_path.replace('http://', '')

        # Upload JSON to Amazon S3
        session = boto3.Session(
            aws_access_key_id=settings.AMAZON_ACCESS_KEY,
            aws_secret_access_key=settings.AMAZON_SECRET_KEY
        )

        s3 = session.resource('s3')

        print("try: s3..upload file: " + local_path)

        try:
            s3.meta.client.upload_file(
                Filename=local_path,
                Bucket=settings.AMAZON_S3_BUCKET,
                Key=remote_path,
                ExtraArgs=extraArgs,
            )

        except boto3.exceptions.S3UploadFailedError:
            print("Error uploading: S3UploadFailed Error")


        print("------Publishing to Cloud: " + remote_path + "-----xyz")

def submit_to_archive_org(url):
    # submit url to archive.org
    if len(url) > 0:
        add_archive_job_to_queue(url)


def add_archive_job_to_queue(url):
    # r = requests.get('https://web.archive.org/save/?url='+ url)
    # r = requests.post('https://web.archive.org/save', data={'url': url})
    print("submit archive request to job queue")


def get_from_cache(filename):

    # Default return dict
    content_dict = {
       'text': '',      # unicode
       'unicode':  '',
       'content':  '',  # raw
       'encoding': '',
       'error': '',
       'language': '',
       'content_type': ''
    }

    # Get the Gzip version of the file
    filename, file_extension = os.path.splitext(filename)
    # if (file_extension != '.gz'):
    #    filename = filename + '.gz'


    # Does a Parent Directory Exist for file Cache?
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except FileNotFoundError:
            pass

    # Was this File already downloaded?  If so, return from cache.
    if os.path.exists(filename):

        try:
            with open(filename, 'r') as content_file:

                file_content = filename.read()

                # Unzip file contents:
                # file_content = gzip.decompress(file_content)

                # Detect Encoding
                blob = open(file_content, 'rb').read()
                m = magic.open(magic.MAGIC_MIME_ENCODING)
                m.load()
                encoding = m.buffer(blob)

                # Get Language
                language = detect(file_content)

                # Get Content Type
                mime = magic.Magic(mime=True)
                content_type = mime.from_file(file_content)  # 'application/pdf'

        except IsADirectoryError:
            # Todo: log exception

            encoding = 'utf-8'
            language = 'en'
            content_type = 'application/html'
            file_content = ''

        content_dict = {
            'text': file_content,        # unicode
            'unicode': file_content,
            'content': file_content,     # raw
            'encoding': encoding,
            'error':  '',
            'language': language,
            'content_type': content_type
        }



    return content_dict
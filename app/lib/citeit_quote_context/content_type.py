from urllib.parse import urlparse


class Content_Type:

    # Distinguish between html, text, .doc, ppt, and pdf
    def doc_type(content_type):

        if (content_type.startswith('text/html') or
                content_type.startswith('application/html')
        ):
            doc_type = 'html'

        elif content_type.startswith('application/pdf'):
            doc_type = 'pdf'

        elif ((content_type == 'text/plain') or
              content_type.startswith('text')
        ):
            doc_type = 'txt'

        elif content_type == 'application/rtf':
            doc_type = 'rtf'

        elif content_type == 'application/epub+zip':
            doc_type = 'epub'

        elif (content_type.startswith('application/msword') or
              content_type.startswith(
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document') or
              content_type.startswith(
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.template') or
              content_type.startswith(
                  'application/vnd.ms-word.document.macroEnabled.12')
        ):
            doc_type = 'doc'

        elif content_type.startswith('application/vnd.ms-powerpoint'):
            doc_type = 'ppt'

        elif content_type == 'audio/mpeg':
            doc_type = 'audio/mpeg'

        elif content_type == 'video/mpeg':
            doc_type = 'video/mpeg'

        elif content_type == 'audio/ogg':
            doc_type = 'audio/ogg'

        elif content_type == 'video/ogg':
            doc_type = 'video/ogg'

        elif content_type == 'application/ogg':
            doc_type = 'audio/ogg'

        elif (content_type == 'audio/wav'):
            doc_type = 'wav'

        elif (content_type == 'audio/aac'):
            doc_type = 'aac'

        elif (content_type == 'image/jpg' or
              content_type == 'image/jpeg'
        ):
            doc_type = 'jpg'

        elif content_type == 'image/png':
            doc_type = 'png'

        elif content_type == 'image/tiff':
            doc_type = 'tiff'

        elif content_type == 'image/webp':
            doc_type = 'webp'

        elif content_type == 'image/gif':
            doc_type = 'gif'

        elif content_type == 'application/vnd.ms-excel':
            doc_type = 'xls'

        elif ((
                      content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') or
              (
                      content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.template')
        ):
            doc_type = 'xlsx'

        elif content_type == 'application/json':
            return 'json'

        else:
            doc_type = 'error: no doc_type: ' + content_type

        return doc_type


    def media_provider(domain):
        domain = urlparse('http://www.example.test/foo/bar').netloc

        if domain == 'www.youtube.com':
            domain = 'youtube'

        elif domain == 'vimeo.com':
            domain = 'vimeo'

        elif domain == 'soundcloud.com':
            domain = 'soundcloud'

        return domain
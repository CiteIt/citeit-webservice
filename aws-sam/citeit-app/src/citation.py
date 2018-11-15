# Copyright (C) 2015-2018 Tim Langeman and contributors
# <see AUTHORS.txt file>
#
# This library is part of the CiteIt project:
# http://www.citeit.net/

# The code for this server library is released under the MIT License:
# http://www.opensource.org/licenses/mit-license

import json

__author__ = 'Tim Langeman'
__email__ = "timlangeman@gmail.com"
__copyright__ = "Copyright (C) 2015-2018 Tim Langeman"
__license__ = "MIT"
__version__ = "0.3"


class Citation:
    """ Find the canonical url within an html document
        Return it if it exists,
        if it does not, return the supplied URL

    """

    def __init__(self, data):
        self.data = data

    def save(self):
        return 1

    def db_save(self):
        """
            Save Quote data to database, using SQLAlchemy
        """
        print("saving to db ..")


    def json_fields(self):
        """
            List of fields to be saved to json and uploaded to cloud
        """
        return [
                'sha256',
                'citing_url', 'citing_quote',
                'citing_context_before', 'citing_context_before',
                'cited_url', 'cited_quote',
                'cited_context_before', 'cited_context_before'
        ]

    def json_data(self):
        """
            Save only specified fields to json
        """
        output = {}
        for field in self.json_fields():
            output[field] = self.data[field]
        return output

    def json_save(self):
        """
            Save json file locally
        """
        print("saving json locally")
        filename = ''.join([self.data['sha256'], '.json'])
        local_filename = ''.join([settings.JSON_FILE_PATH, filename])

        with open(local_filename, 'w') as outfile:
            json.dump(self.json_data(), outfile, indent=4, ensure_ascii=False)

    def json_upload(self):
        """
            Upload json file to cloud
        """
        print("uploading json to cloud")
        return 1

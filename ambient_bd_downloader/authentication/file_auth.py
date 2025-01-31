import logging
import os

from requests.auth import HTTPBasicAuth

# to prevent committing passwords to github users credentials are read from a file outside git
# and returned as BasicAuth objects.

# Prompt for username and password
# username = input("Enter username: ")
# password = getpass.getpass("Enter password: ")


class SimpleFileAuth:
    def __init__(self, file_path='./auth.tsv'):
        self._logger = logging.getLogger(__name__)
        self.file_path = file_path
        # log the absolute path to the auth file
        self._logger.info(f'Using auth file: {os.path.abspath(file_path)}')

    def get_auth(self, user_nr=0):
        credentials = self._read_credentials()
        if user_nr >= len(credentials):
            raise ValueError(f'User number {user_nr} is out of range. Number of users: {len(credentials)}')

        user = credentials[user_nr]
        auth = HTTPBasicAuth(user['username'], user['password'])
        return auth

    def _read_credentials(self):
        credentials = []
        with open(self.file_path, 'r') as file:
            for line in file:
                username, password = line.strip().split('\t')
                user_dict = {'username': username, 'password': password}
                credentials.append(user_dict)
        return credentials

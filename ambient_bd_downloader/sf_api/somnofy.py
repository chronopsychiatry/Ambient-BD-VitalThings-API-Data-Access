import datetime
from requests_oauthlib import OAuth2Session
from os.path import join, exists, dirname
from os import urandom, remove
import base64
import hashlib
import webbrowser
import logging

from ambient_bd_downloader.sf_api.dom import Subject, Session

# API
# https://api.health.somnofy.com/api/v1/docs#/


class Somnofy:
    def __init__(self, properties, zone):
        self._logger = logging.getLogger('Somnofy')
        self.client_id = properties.client_id
        if not self.client_id:
            raise ValueError('Client ID must be provided')
        self.token_file = join(dirname(properties.client_id_file), 'token.txt')
        self.subjects_url = 'https://api.health.somnofy.com/api/v1/subjects'
        self.sessions_url = 'https://api.health.somnofy.com/api/v1/sessions'
        self.reports_url = 'https://api.health.somnofy.com/api/v1/reports'
        self.zones_url = 'https://api.health.somnofy.com/api/v1/zones'
        self.devices_url = 'https://api.health.somnofy.com/api/v1/devices'
        self.date_start = '2023-08-01T00:00:00Z'
        self.date_end = datetime.datetime.now().isoformat()
        self.LIMIT = 300
        self.oauth = self.set_auth(properties.client_id)
        self.zone_name = zone
        self.zone_id = self.get_zone_id()

    def set_auth(self, client_id: str):
        if exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token = f.read()
            oauth = OAuth2Session(client_id, token={'access_token': token, 'token_type': 'Bearer'})
            r = oauth.get(self.subjects_url)  # Test if the token is still valid
            if r.status_code == 200:
                self._logger.info('Accessing API with stored token.')
                return oauth
            else:
                remove(self.token_file)
                print('Token is no longer valid. Please reauthorize.')

        # Generate a code verifier and code challenge
        code_verifier = base64.urlsafe_b64encode(urandom(40)).rstrip(b'=').decode('utf-8')
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8'))
                                                  .digest()).rstrip(b'=').decode('utf-8')
        # Create an OAuth2 session
        oauth = OAuth2Session(client_id, redirect_uri='https://api.health.somnofy.com/oauth2-redirect')
        # Redirect user to Somnofy's authorization URL
        authorization_url, state = oauth.authorization_url('https://auth.somnofy.com/oauth2/authorize',
                                                           code_challenge=code_challenge,
                                                           code_challenge_method='S256')
        print('Please authorize access in your web browser.')
        webbrowser.open(authorization_url)
        # Get the authorization response URL from the user
        authorization_response = input('Enter the full URL: ')
        # Fetch the access token
        token = oauth.fetch_token('https://auth.somnofy.com/oauth2/token',
                                  authorization_response=authorization_response,
                                  include_client_id=True,
                                  code_verifier=code_verifier)
        with open(self.token_file, 'w') as f:
            f.write(token['access_token'])
        return oauth

    def get_subjects(self):
        r = self.oauth.get(self.subjects_url, params={'path': self.zone_id, 'embed': 'devices'})
        json_list = r.json()["data"]
        return [Subject(subject_data) for subject_data in json_list]

    def select_subjects(self, subject_name, device_name):
        subjects = self.get_subjects()
        selected_subjects = []
        for subject in subjects:
            if ((subject.identifier in subject_name or '*' in subject_name)
                    and (subject.device in device_name or '*' in device_name)):
                selected_subjects.append(subject)
        return selected_subjects

    def _make_sessions_params(self, limit=None, from_date=None, to_date=None):
        if limit is None:
            limit = self.LIMIT
        if from_date is None:
            from_date = self.date_start
        if to_date is None:
            to_date = self.date_end

        # if data is passed to params as an object, the API does not take time part of the timestamp
        # and all sessions from the start date are turned
        # if start_time is explicitly converted to string than API behaves as expected
        if isinstance(from_date, datetime.datetime):
            from_date = from_date.isoformat()
        if isinstance(to_date, datetime.datetime):
            to_date = to_date.isoformat()

        return {
            'limit': limit,
            'from': from_date,
            'to': to_date,
            'sort': 'asc'
        }

    def get_all_sessions_for_subject(self, subject_id, from_date=None, to_date=None):
        params = self._make_sessions_params(from_date=from_date, to_date=to_date)
        params['subject_id'] = subject_id
        params['type'] = 'vitalthings-somnofy-sm100-session'
        are_more = True
        sessions = []
        while are_more:
            r = self.oauth.get(self.sessions_url, params=params)
            json_list = r.json()['data']
            sessions += [Session(data) for data in json_list]
            are_more = len(json_list) == self.LIMIT
            if are_more:
                params['from'] = datetime.datetime.fromisoformat(json_list[-1]['session_start'])
        return sessions

    def get_session_json(self, session_id):
        url = f'{self.sessions_url}/{session_id}'
        params = {'include_epoch_data': True}
        r = self.oauth.get(url, params=params)
        return r.json()

    def get_session_report(self, subject_id, date):
        params = {'subjects': subject_id, 'report_date': date}
        r = self.oauth.get(self.reports_url, params=params)
        return r.json()

    def get_zone_id(self):
        r = self.oauth.get(self.zones_url)
        zone_names = []
        for zone in r.json()['data']:
            zone_names.append(zone['name'])
            if zone['name'] == self.zone_name:
                return zone['id']
        raise ValueError(f'Zone "{self.zone_name}" not found. Available zones: {zone_names}')

    def has_zone_access(self):
        zone_id = self.get_zone_id()
        r = self.oauth.get(self.subjects_url, params={'path': zone_id})
        return True if r.status_code == 200 else False

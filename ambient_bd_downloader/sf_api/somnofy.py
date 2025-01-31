import datetime
import requests
from requests.auth import HTTPBasicAuth

from ambient_bd_downloader.sf_api.dom import User, Session

# API
# https://static.vitalthings.com/somnofy/docs/api/74640730-42fa-486c-996d-6bda9b042a96.html?python#somnofy-partner-api-users
# https://api.health.somnofy.com/api/v1/openapi.json

OUTPUTS = [
    'environment',
    'vitalsigns',
    'sleep_analysis.report',
    'sleep_analysis.hypnogram',
    'sleep_analysis.meta',
    'sleep_analysis.epoch_data'
]

SESSION_DATA_OUTPUTS = [OUTPUTS[2], OUTPUTS[3], OUTPUTS[5]]
SESSION_REPORT_OUTPUT = [OUTPUTS[2]]


class Somnofy:
    def __init__(self, auth: HTTPBasicAuth = None, user: str = None, password: str = None):
        self.auth = auth
        if (not auth) and user and password:
            self.auth = HTTPBasicAuth(user, password)
        if not self.auth:
            raise ValueError('auth or user and password must be provided')
        self.users_url = 'https://partner.api.somnofy.com/v1/users'
        self.sessions_url = 'https://partner.api.somnofy.com/v1/sessions'
        self.date_start = '2023-08-01T00:00:00Z'
        self.date_end = datetime.datetime.now().isoformat()
        self.LIMIT = 50

    def get_users(self):
        headers = {'Accept': 'application/json'}
        r = requests.get(self.users_url, params={}, headers=headers, auth=self.auth)
        print(r.json())
        json_list = r.json()["_embedded"]["users"]
        return [User(user_data) for user_data in json_list]

    def _make_sessions_params(self, offset=0, limit=None, from_date=None, to_date=None):
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
            'offset': offset,
            'sort': 'asc'
        }

    def get_all_sessions_for_user(self, user_id, from_date=None, to_date=None):

        headers = {'Accept': 'application/json'}
        offset = 0
        params = self._make_sessions_params(offset, from_date=from_date, to_date=to_date)
        are_more = True
        sessions = []
        while are_more:
            params['offset'] = offset
            params['user_id'] = user_id
            r = requests.get(self.sessions_url, params=params, headers=headers, auth=self.auth)
            json_list = r.json()["_embedded"]["sessions"]
            offset += len(json_list)
            sessions += [Session(data) for data in json_list]
            are_more = len(json_list) > 0 and not (sessions[-1].state == 'IN_PROGRESS')
        return sessions

    def get_session_json(self, session_id, user_id, embeds=SESSION_DATA_OUTPUTS):
        headers = {'Accept': 'application/json'}
        params = {
            'user_id': user_id,
            'embed': embeds
        }
        url = f'{self.sessions_url}/{session_id}'
        r = requests.get(url, params=params, headers=headers, auth=self.auth)
        return r.json()

    def get_session_report(self, session_id, user_id):
        return self.get_session_json(session_id, user_id, embeds=SESSION_REPORT_OUTPUT)

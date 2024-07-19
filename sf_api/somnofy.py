import datetime
import requests

from sf_api.dom import User, Session

users_url = 'https://partner.api.somnofy.com/v1/users'
sessions_url = 'https://partner.api.somnofy.com/v1/sessions'

date_start = '2023-08-01T00:00:00Z'
date_end = datetime.datetime.now().isoformat()

LIMIT = 50


def get_users(auth):
    headers = {
        'Accept': 'application/json'
    }

    r = requests.get(users_url, params={}, headers=headers, auth=auth)

    json_list = r.json()["_embedded"]["users"]

    users = [User(user_data) for user_data in json_list]
    return users


def make_sessions_params(offset=0, limit=LIMIT, from_date=date_start, to_date=date_end):
    return {
        'limit': limit,
        'from': from_date,
        'to': to_date,
        'offset': offset,
        'sort': 'asc'

    }


def get_all_sessions_for_user(user_id, auth, from_date=date_start, to_date=date_end):
    headers = {
        'Accept': 'application/json'
    }
    offset = 0
    are_more = True
    sessions = []
    while are_more:


        params = make_sessions_params(offset, from_date=from_date, to_date=to_date)
        params['user_id'] = user_id
        r = requests.get(sessions_url, params=params, headers=headers, auth=auth)

        json_list = r.json()["_embedded"]["sessions"]
        offset += len(json_list)

        sessions += [Session(data) for data in json_list]
        are_more = len(json_list) > 0 and not (sessions[-1].state == 'IN_PROGRESS')
    return sessions


outputs = [
    'environment',
    'vitalsigns',
    'sleep_analysis.report',
    'sleep_analysis.hypnogram',
    'sleep_analysis.meta',
    'sleep_analysis.epoch_data'

]

session_data_outputs = [outputs[2], outputs[3], outputs[5]]
session_report_outputs = [outputs[2]]

def get_session_json(session_id, user_id, auth, embeds = session_data_outputs):
    headers = {
        'Accept': 'application/json'
    }


    params = {

        # 'limit': 2,
        # 'from': '2024-02-12T00:00:00',
        # 'to': '2024-02-13T00:00:00', #outputs[0], outputs[1],
        'user_id': user_id,
        'embed': embeds
    }

    url = sessions_url + '/' + session_id
    r = requests.get(url, params=params, headers=headers, auth=auth)
    return r.json()

def get_session_report(session_id, user_id, auth):
    return get_session_json(session_id, user_id, auth, embeds=session_report_outputs)
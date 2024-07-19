import datetime
import json
import os
from typing import Union

import pandas as pd
import logging

from paths_resolver import PathsResolver
from sessions_info import make_epoch_data_frame_from_session
from sf_api.somnofy import get_all_sessions_for_user, get_session_json, get_session_report

out_dir = './data'





class DataDownloader:
    def __init__(self, resolver = PathsResolver()):
        self.resolver = resolver
        self.logger = logging.getLogger(__name__)

    def download_user_data(self, auth, user_id, start_date = None):

        start_date = start_date or self.get_date_from_last_session(user_id)

        sessions = get_all_sessions_for_user(user_id, auth, start_date)
        # print(f'Found {len(sessions)} sessions for user {user_id} between {start_date} and now')

        if len(sessions) == 0:
            self.logger.info(f'No sessions found for user {user_id} between {start_date} and now')
            return None


        reports = pd.DataFrame()

        last_session = None

        for s in sessions:
            if s.state == 'IN_PROGRESS':
                self.logger.debug(f'Skipping session {s.session_id} for user {user_id} as it is in progress')
                continue
                
            self.logger.info(f'Downloading session {s.session_id} for user {user_id}')

            s_json = get_session_json(s.session_id, user_id, auth)
            self.save_raw_session_data(s_json, user_id, s.session_id)

            #df = make_epoch_data_frame_from_session(s_json)
            #path = os.path.join(user_dir, f'{s.session_id}_session_data.csv')
            #df.to_csv(path, index=False)

            #df = pd.DataFrame(s_json['_embedded']['sleep_analysis']['report'], index=[0])
            # add as first column the session_id
            #df.insert(0, 'session_id', s.session_id)
            #reports = pd.concat([reports, df], ignore_index=True)

            last_session = s_json

        if last_session:
            last_session['_embedded'] = []
            with open(self.resolver.get_user_last_session(user_id), 'w') as f:
                json.dump(last_session, f)

        #path = os.path.join(user_dir, 'sessions_reports.csv')
        #reports.to_csv(path, index=False)
        #return user_dir

    def get_date_from_last_session(self, user_id):
        session_file = self.resolver.get_user_last_session(user_id)
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session = json.load(f)
                return datetime.datetime.fromisoformat(session['end_time'])
        else:
            raise ValueError(f'No last session found for user {user_id} and no start date provided')

    def save_raw_session_data(self, s_json, user_id, session_id):

        start_date = datetime.datetime.fromisoformat(s_json['start_time']).date()

        path = os.path.join(self.resolver.get_user_raw_dir(user_id), f'{start_date}_{session_id}_raw.json')
        with open(path, 'w') as f:
            json.dump(s_json, f)


def set_out_dir(path):
    global out_dir

    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.isdir(path):
            raise ValueError(f'{path} is not a directory')

    out_dir = path

def get_out_dir():
    return out_dir


def download_user_data(user_id, auth,
                       filter_shorter_than_hours: Union[int, bool] = 2,
                       from_date: datetime.date = (datetime.datetime.now() - datetime.timedelta(7)).date(),
                       to_date: datetime.date = datetime.datetime.now().date()):


    sessions = get_all_sessions_for_user(user_id, auth, from_date, to_date)
    if len(sessions) == 0:
        raise ValueError(f'No sessions found for user {user_id} between {from_date} and {to_date}')

    user_dir = os.path.join(out_dir, user_id)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    reports = pd.DataFrame()

    for s in sessions:

        if filter_shorter_than_hours and not s.duration_seconds or s.duration_seconds < filter_shorter_than_hours * 3600:
            s_json = get_session_report(s.session_id, user_id, auth)
        else:
            s_json = get_session_json(s.session_id, user_id, auth)
            df = make_epoch_data_frame_from_session(s_json)
            path = os.path.join(user_dir, f'{s.session_id}_session_data.csv')
            df.to_csv(path, index=False)

        df = pd.DataFrame(s_json['_embedded']['sleep_analysis']['report'], index=[0])
        # add as first column the session_id
        df.insert(0, 'session_id', s.session_id)
        reports = pd.concat([reports, df], ignore_index=True)

    path = os.path.join(user_dir, 'sessions_reports.csv')
    reports.to_csv(path, index=False)
    return user_dir


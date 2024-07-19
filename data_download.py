import datetime
import json
import os
from typing import Union

import pandas as pd

import logging

from paths_resolver import PathsResolver
from sf_api.somnofy import Somnofy


class DataDownloader:
    def __init__(self, somnofy: Somnofy, resolver = PathsResolver()):
        if not somnofy:
            raise ValueError('Somnofy connection must be provided')
        self.somnofy = somnofy
        self.resolver = resolver
        self.logger = logging.getLogger(__name__)
        self.filter_shorter_than_hours = 2

    def save_user_data(self, user_id, start_date = None):

        start_date = start_date or self.get_date_from_last_session(user_id)

        sessions = self.somnofy.get_all_sessions_for_user(user_id, start_date)
        # print(f'Found {len(sessions)} sessions for user {user_id} between {start_date} and now')

        if len(sessions) == 0:
            self.logger.info(f'No sessions found for user {user_id} between {start_date} and now')
            return None

        reports = pd.DataFrame()
        epoch_data = pd.DataFrame()

        last_session = None
        last_session_json = None

        for s in sessions:
            if self.is_in_progress(s, user_id):
                continue

            self.logger.info(f'Downloading session {s.session_id} for user {user_id}')

            s_json = self.somnofy.get_session_json(s.session_id, user_id)
            self.save_raw_session_data(s_json, user_id, s.session_id)

            reports = pd.concat([reports, self.make_session_report(s_json)], ignore_index=True)

            if self.should_store_epoch_data(s):
                epoch_data = pd.concat([epoch_data, self.make_epoch_data_frame_from_session(s_json)], ignore_index=True)

            last_session = s
            last_session_json = s_json

        self.save_reports(reports, user_id, sessions,last_session)
        self.append_to_global_reports(reports, user_id)
        self.save_epoch_data(epoch_data, user_id, sessions,last_session)
        self.save_last_session(last_session_json, user_id)


    def should_store_epoch_data(self, session):
        return not self.filter_shorter_than_hours or not session.duration_seconds or session.duration_seconds > self.filter_shorter_than_hours * 60 * 60

    def make_session_report(self, s_json):
        df = pd.DataFrame(s_json['_embedded']['sleep_analysis']['report'], index=[0])
        df.insert(0, 'session_id', s_json['session_id'])
        return df

    def is_in_progress(self, session, user_id):
        if session.state == 'IN_PROGRESS':
            self.logger.debug(f'Skipping session {session.session_id} for user {user_id} as it is in progress')
            return True
        return False

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

    def save_last_session(self, last_session_json, user_id):
        if last_session_json:
            last_session_json['_embedded'] = []
            path = self.resolver.get_user_last_session(user_id)
            with open(path, 'w') as f:
                json.dump(last_session_json, f)

    def save_reports(self, reports, user_id, sessions, last_session):
        if len(sessions) == 0:
            return
        if not last_session:
            return

        dates = self.sessions_to_date_range(sessions[0], last_session)

        file_name = f'{dates[0]}_{dates[1]}_sessions_reports.csv'
        user_dir = self.resolver.get_user_data_dir(user_id)
        path = os.path.join(user_dir, file_name)
        reports.to_csv(path, index=False)

    def sessions_to_date_range(self, first_session, last_session):
        start_date = first_session.start_time.date()
        end_date = last_session.end_time.date()
        return start_date, end_date

    def save_epoch_data(self, epoch_data, user_id, sessions, last_session):
        if len(sessions) == 0:
            return
        if not last_session:
            return

        dates = self.sessions_to_date_range(sessions[0], last_session)

        file_name = f'{dates[0]}_{dates[1]}_epoch_data.csv'
        user_dir = self.resolver.get_user_data_dir(user_id)
        path = os.path.join(user_dir, file_name)
        epoch_data.to_csv(path, index=False)

    def make_epoch_data_frame_from_session(self,session_json: dict) -> pd.DataFrame:
        """
        Make a DataFrame from a session
        :param session_json: json data for session
        :return: DataFrame with session data
        """
        epoch_data = pd.DataFrame(session_json['_embedded']['sleep_analysis']['epoch_data'])
        epoch_hypnogram = pd.DataFrame(session_json['_embedded']['sleep_analysis']['hypnogram'])

        # check if both has same number of rows, throw exception when not met with actual numbers
        if len(epoch_data) != len(epoch_hypnogram):
            raise Exception(
                f"Epoch data and hypnogram data have different number of rows: {len(epoch_data)} vs {len(epoch_hypnogram)}")

        session_data = pd.concat([epoch_hypnogram, epoch_data], axis=1)

        # add session_id as first column
        session_data.insert(0, 'session_id', session_json['session_id'])

        # change the order of columns that first is 'timestamp' and then rest remains same
        session_data = session_data[['timestamp'] + [col for col in session_data.columns if col != 'timestamp']]
        return session_data

    def append_to_global_reports(self, reports, user_id):
        file = self.resolver.get_user_global_report(user_id)
        reports.to_csv(file, mode='a', header=not os.path.exists(file), index=False)


'''
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

'''
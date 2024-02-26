import datetime
import os
from typing import Union

import pandas as pd

from sessions_info import make_data_frame_from_session
from sf_api.somnofy import get_all_sessions_for_user, get_session_json, get_session_report

out_dir = './data'

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
            df = make_data_frame_from_session(s_json)
            path = os.path.join(user_dir, f'{s.session_id}_session_data.csv')
            df.to_csv(path, index=False)

        df = pd.DataFrame(s_json['_embedded']['sleep_analysis']['report'], index=[0])
        # add as first column the session_id
        df.insert(0, 'session_id', s.session_id)
        reports = pd.concat([reports, df], ignore_index=True)

    path = os.path.join(user_dir, 'sessions_reports.csv')
    reports.to_csv(path, index=False)
    return user_dir


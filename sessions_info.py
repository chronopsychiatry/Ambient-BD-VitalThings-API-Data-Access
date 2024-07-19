from itertools import groupby

import pandas as pd
from pandas import DataFrame

from sf_api.dom import Session


def group_sessions_by_enddate(sessions: [Session]) -> dict:
    """
    Group sessions by end date
    :param sessions: list of sessions
    :return: dictionary with end date as key and list of sessions as value
    """

    # sort sessions by end time as group by needs sorted keys!
    sessions = sorted(sessions, key=lambda x: x.end_time)
    return {k: list(v) for k, v in groupby(sessions, lambda x: x.end_time.date())}

def calculate_aggregated_sessions_stats(groups: dict) -> dict:
    """
    Calculate aggregated stats for each group of sessions
    :param groups: dictionary with end date as key and list of sessions as value
    :return: dictionary with end date as key and aggregated stats as value
    """
    aggregated_values = {}

    for end_date, sessions in groups.items():
        total_duration = sum(session.duration_seconds for session in sessions)
        num_sessions = len(sessions)
        max_duration = max(session.duration_seconds for session in sessions)
        device_serial_number = sessions[0].device_serial_number
        user_id = sessions[0].user_id

        aggregated_values[end_date] = {
            'total_duration': total_duration,
            'num_sessions': num_sessions,
            'max_duration': max_duration,
            'device_serial_number': device_serial_number,
            'user_id': user_id
        }
    return aggregated_values

def mark_valid_nights(per_date: dict) -> dict:
    """
    Mark days with valid number of sessions
    :param per_date: dictionary with end date as key and aggregated stats as value
    :return: dictionary with end date as key and aggregated stats as value with valid field
    """
    for date, stats in per_date.items():
        stats['valid'] = stats['max_duration'] > 3*3600
    return per_date

def make_epoch_data_frame_from_session(session_json: dict) -> DataFrame:
    """
    Make a DataFrame from a session
    :param session_json: json data for session
    :return: DataFrame with session data
    """
    epoch_data = DataFrame(session_json['_embedded']['sleep_analysis']['epoch_data'])
    epoch_hypnogram = DataFrame(session_json['_embedded']['sleep_analysis']['hypnogram'])

    #check if both has same number of rows, throw exception when not met with actual numbers
    if len(epoch_data) != len(epoch_hypnogram):
        raise Exception(f"Epoch data and hypnogram data have different number of rows: {len(epoch_data)} vs {len(epoch_hypnogram)}")

    session_data = pd.concat([epoch_hypnogram, epoch_data ], axis=1)

    # add session_id as first column
    session_data.insert(0, 'session_id', session_json['session_id'])

    # change the order of columns that first is 'timestamp' and then rest remains same
    session_data = session_data[['timestamp'] + [col for col in session_data.columns if col != 'timestamp']]
    return session_data


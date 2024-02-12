from itertools import groupby

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


        aggregated_values[end_date] = {
            'total_duration': total_duration,
            'num_sessions': num_sessions,
            'max_duration': max_duration,
        }
    return aggregated_values

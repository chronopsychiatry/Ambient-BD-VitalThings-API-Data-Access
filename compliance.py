import datetime

from pandas import DataFrame, pandas

from sessions_info import *
from sf_api.dom import User
from sf_api.somnofy import Somnofy


def get_user_nights(somnofy: Somnofy, user: User, from_date: datetime.date, to_date: datetime.date) -> dict:

    to_date += datetime.timedelta(days=1) # add one day to the to_date to include the last day
    sessions = somnofy.get_all_sessions_for_user(user.id, from_date=from_date.isoformat(), to_date=to_date.isoformat())
    sessions = [s for s in sessions if s.state != 'IN_PROGRESS']

    groups = group_sessions_by_enddate(sessions)
    per_date = calculate_aggregated_sessions_stats(groups)
    per_date = mark_valid_nights(per_date)

    valid_nights = len([day for day, stat in per_date.items() if stat['valid']])
    user.valid_nights = valid_nights

    return per_date



def get_dates_between(start_date: datetime.date, end_date: datetime.date) -> [datetime.date]:

    dates_between = []

    # Iterate over the range of dates and add them to the list
    current_date = start_date
    while current_date <= end_date:
        dates_between.append(current_date)
        current_date += datetime.timedelta(days=1)

    return dates_between

def get_device_serial_number(nights: []) -> str:
    #if nights is empty return None else return the device serial number of the first night
    return next(iter(nights.values()))['device_serial_number'] if nights else None


def build_user_nights_dataframe(users_nights: dict, dates: [datetime.date]) -> DataFrame:

    df = DataFrame()

    for user, nights in users_nights.items():
        row = { 'user_id': user.id,
                'device_serial_number': get_device_serial_number(nights),
                'valid_nights': user.valid_nights
              }

        for date in dates:
            if date in nights:
                row[date] = nights[date]['max_duration']/3600
            else:
                row[date] = 'NaN'

        df = pandas.concat([df, DataFrame(row, index=[0])], ignore_index=True)
    return df


def calculate_compliance(auth, users: [User] = [],
                         from_date: datetime.date = (datetime.datetime.now() - datetime.timedelta(7)).date,
                         to_date: datetime.date = datetime.datetime.now().date(),
                         ) -> DataFrame:

    users_nights = {}

    for u in users:
        nights = get_user_nights(auth, u, from_date, to_date)
        users_nights[u] = nights

    # order users_nights by user property valid_nights
    users_nights = dict(sorted(users_nights.items(), key=lambda item: item[0].valid_nights, reverse=False))

    dates = get_dates_between(from_date, to_date)

    return build_user_nights_dataframe(users_nights, dates)


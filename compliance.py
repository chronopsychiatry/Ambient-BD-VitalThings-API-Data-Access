import datetime

import pandas as pd
from pandas import DataFrame, pandas

from sessions_info import *
from sf_api.dom import User
from sf_api.somnofy import Somnofy

class ComplianceChecker:

    def aggregate_session_records(self, records: DataFrame) -> DataFrame:

        records['session_end'] = pd.to_datetime(records['session_end'])
        records['night_date'] = records['session_end'].dt.date

        stats = records.groupby('night_date').agg(
            number_of_long_sessions=('session_id', 'count'),
            max_time_asleep_h=('time_asleep', 'max')
        ).reset_index()

        stats['max_time_asleep_h'] = (stats['max_time_asleep_h'] / 3600).round(2)
        stats['valid'] = stats['max_time_asleep_h'] > 3


        return stats

    def add_missing_nights(self, compliance_info, start_date, end_date) -> DataFrame:

        # if end_date is not a datetime object, convert it to one
        if not isinstance(end_date, datetime.date):
            end_date = pd.to_date(end_date)
        if not isinstance(start_date, datetime.date):
            start_date = pd.to_date(start_date)

        range = set(pd.date_range(start_date, end_date, freq='D').date)
        missing_dates = range.difference(compliance_info['night_date'])

        missing_nights = pd.DataFrame(missing_dates, columns=['night_date'])
        missing_nights['valid'] = False
        missing_nights['number_of_long_sessions'] = 0
        missing_nights['max_time_asleep_h'] = 0

        stats = pd.concat([compliance_info, missing_nights], ignore_index=True)
        return stats

    def calculate_compliance(self, records: DataFrame, dates) -> DataFrame:
        start_date = dates[0]
        end_date = dates[1]

        compliance_info = self.aggregate_session_records(records)
        compliance_info = self.add_missing_nights(compliance_info, start_date, end_date)
        compliance_info = compliance_info.sort_values('night_date', ascending=True)

        return compliance_info

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


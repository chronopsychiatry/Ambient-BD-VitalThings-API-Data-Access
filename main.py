# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import pandas as pd
import datetime

from compliance import calculate_compliance, get_user_nights
from local_auth import get_auth
from sessions_info import calculate_aggregated_sessions_stats, group_sessions_by_enddate, mark_valid_nights
from sf_api.dom import User
from sf_api.somnofy import get_users, get_all_sessions_for_user


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Function to parse timestamps into datetime objects
def parse_timestamps(json_obj):
    json_obj["end_time"] = datetime.datetime.fromisoformat(json_obj["end_time"])
    json_obj["start_time"] = datetime.datetime.fromisoformat(json_obj["start_time"])
    json_obj["duration"] = (json_obj['end_time'] - json_obj['start_time']).total_seconds()
    return json_obj

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/

    headers = {
        'Accept': 'application/json'
    }

    basic = get_auth(1)
    print("Accessing somnofy with user: {}".format(basic.username))
    #r = requests.get('https://partner.api.somnofy.com/v1/users', params={}, headers=headers, auth=basic)
    #print(json.dumps(r.json(), indent=2))

    #href = 'https://api.somnofy.com/v1/sessions?user_id=65367bfb2b751b0013e9bebf'
    #r = requests.get(href, headers=headers, auth=basic)

    params = {
              'limit' : 2,
              'from': '2023-08-01T00:00:00Z',
              'to': '2024-01-15T00:00:00Z',
              'embed': ['sleep_analysis.report','sleep_analysis.epoch_data']
              }

    #params = {
    #    'user_id':'65367bfb2b751b0013e9bebf'
    #}
    #href = 'https://partner.api.somnofy.com/v1/sessions'
    #r = requests.get(href, params=params, headers=headers, auth=basic)

    from_date = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()


    users = get_users(basic)
    for u in users:
        print(u)

    user_id = '64d22532c58c030014afb890'

    # make date from string    '2023-08-01T00:00:00Z'
    #start_date = datetime.datetime.fromisoformat('2024-02-12T00:00:00').date()
    #end_date = datetime.datetime.fromisoformat('2024-02-12T00:00:00').date()
    start_date = '2024-02-12T00:00:00'
    end_date = '2024-02-13T00:00:00'

    sessions = get_all_sessions_for_user(user_id, basic, start_date, end_date)

    for s in sessions:
        print("{} {}".format(s.session_id, s.duration_seconds))

    for x in range(0,1):
        s = sessions[4]
        print(s)

        outputs = [
            'environment',
            'vitalsigns',
            'sleep_analysis.report',
            'sleep_analysis.hypnogram',
            'sleep_analysis.meta',
            'sleep_analysis.epoch_data'

        ]
        params = {

                  'limit' : 2,
                    'user_id': user_id,
                    'from': '2024-02-12T00:00:00',
                    'to': '2024-02-13T00:00:00', #outputs[0], outputs[1],
                  'embed': [outputs[3], outputs[5]
                 ]}

        url = "https://partner.api.somnofy.com/v1/sessions/" + s.session_id
        print(url)

        r = requests.get(url,params=params, headers=headers, auth=basic)

        #print(json.dumps(r.json(), indent=2))

        print(
            r.json()['_embedded']['sleep_analysis'].keys()
        )

        print(
            r.json()['_embedded']['sleep_analysis']['epoch_data'].keys()
        )
        print(len(r.json()['_embedded']['sleep_analysis']['epoch_data']))
        df = pd.DataFrame(r.json()['_embedded']['sleep_analysis']['epoch_data'])

        print( 
            r.json()['_embedded']['sleep_analysis']['hypnogram'].keys()
        )
        df = pd.DataFrame(r.json()['_embedded']['sleep_analysis']['hypnogram'])
        #print(df)
        df.to_csv('session_data.csv', index=False)

    # groups = group_sessions_by_enddate(sessions)
    # per_date = calculate_aggregated_sessions_stats(groups)
    # for k,v in per_date.items():
    #     print(k,v)
    #
    # v = per_date[ datetime.datetime.fromisoformat('2023-11-21T00:00:00').date()]
    # print(v)
    #
    #
    # u = User({'id': '65367bfb2b751b0013e9bebf', 'created_at': '2023-08-01T00:00:00Z'})
    # per_date = get_user_nights(basic, u, start_date, end_date)
    # print(per_date)
    # for k,v in per_date.items():
    #     print(k,v)


    ## making usage table
    # usage_table = calculate_compliance(basic, users, from_date=start_date, to_date=end_date)
    #
    # # usage_table.to_csv('session_data.csv', index=False)
    # print(usage_table)



    #for u in users:
        #print(f"User {u}")


        #sessions = get_all_sessions_for_user(u.id, basic, from_date=from_date)
        # remove sessions with state IN_PROGRESS
        #sessions = [s for s in sessions if s.state != 'IN_PROGRESS']


        #per_day = calculate_aggregated_sessions_stats(group_sessions_by_enddate(sessions))

        #days = len(per_day)
        #print("Days: {}".format(days))

        #ark_valid_nights(per_day)

        #for day, stat in per_day.items():
        #    print("{}: {}".format(day,stat))

        # filter out the valid days
        #valid_days = {day: stat for day, stat in per_day.items() if stat['valid']}
        #print("Valid Days: {} out of {}".format(len(valid_days), len(per_day)))


        #for s in sessions:
        #    print("{} {} {} {}".format(s.session_id, s.state, s.start_time, s.end_time))

        #long = [s for s in sessions if s.duration_seconds and s.duration_seconds > 3*60*60]

        #days = {session.start_time.date() for session in sessions}
        #print("Sessions {}, Over hours {} Days {}".format(len(sessions),len(long),len(days)))

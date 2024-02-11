# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import pandas as pd
import datetime
from local_auth import get_auth
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
    r = requests.get('https://partner.api.somnofy.com/v1/users', params={}, headers=headers, auth=basic)

    print(json.dumps(r.json(), indent=2))

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
    href = 'https://partner.api.somnofy.com/v1/sessions'
    #r = requests.get(href, params=params, headers=headers, auth=basic)

    print("\n------------Sessions information---------------")
    #print(json.dumps(r.json(), indent=2))

    print("\n------------Sessions information2 ---------------")

    params = {
              'limit' : 200,
              'from': '2023-08-01T00:00:00Z',
              'to': '2024-01-15T00:00:00Z',
              'offset': 0,
              #'embed': ['sleep_analysis.report','sleep_analysis.epoch_data']
              }

    #href = 'https://api.somnofy.com/v1/sessions?user_id=63079b5951f74a0018edac6d'
    href = 'https://api.somnofy.com/v1/sessions?user_id=65367bfb2b751b0013e9bebf'
    r = requests.get(href, params=params, headers=headers, auth=basic)

    print("\n------------Sessions information---------------")
    print(json.dumps(r.json(), indent=2))

    print("\n------------Sessions details ---------------")
    print(type(r.json()["_embedded"]["sessions"]))
    print("Sessions {}".format(len(r.json()["_embedded"]["sessions"])))

    tab = pd.json_normalize(r.json()["_embedded"]["sessions"])
    print(type(tab))
    print(tab.head())



    # Parse timestamps in all JSON objects
    #json_list_parsed = [parse_timestamps(json_obj) for json_obj in r.json()["_embedded"]["sessions"]]

    # Create a DataFrame
    #df = pd.DataFrame(json_list_parsed)

    # Selecting required columns
    #df = df[['session_id', 'device_serial_number', 'duration', 'start_time','end_time',  'state', 'user_id']]

    # Display the DataFrame
    #df.sort_values(by='start_time', inplace=True)
    #print(df)
    #print(df.iloc[0])
    #print(df.iloc[1])

    #df.to_csv('session_data.csv', index=False)

    users = get_users(basic)
    for u in users:
        print(u)
        sessions = get_all_sessions_for_user(u.id, basic)
        #for s in sessions:
        #    print("{} {} {} {}".format(s.session_id, s.state, s.start_time, s.end_time))

        long = [s for s in sessions if s.duration_seconds and s.duration_seconds > 3*60*60]

        days = {session.start_time.date() for session in sessions}
        print("Sessions {}, Over hours {} Days {}".format(len(sessions),len(long),len(days)))

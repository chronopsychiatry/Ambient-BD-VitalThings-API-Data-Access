# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
from local_auth import get_auth

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # See PyCharm help at https://www.jetbrains.com/help/pycharm/

    headers = {
        'Accept': 'application/json'
    }

    basic = get_auth()
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
    r = requests.get(href, params=params, headers=headers, auth=basic)

    print("\n------------Sessions information---------------")
    print(json.dumps(r.json(), indent=2))

    href = 'https://api.somnofy.com/v1/sessions?user_id=63079b5951f74a0018edac6d'
    r = requests.get(href, headers=headers, auth=basic)

    print("\n------------Sessions information---------------")
    print(json.dumps(r.json(), indent=2))

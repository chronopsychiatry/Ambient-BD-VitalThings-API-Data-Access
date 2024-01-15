from requests.auth import HTTPBasicAuth

# to prevent commiting passwords to github users credentials are read from a file outside git
# and returned as BasicAuth objects.


def read_credentials(file_path):
    credentials = []

    with open(file_path, 'r') as file:
        for line in file:
            username, password = line.strip().split('\t')

            # Create a dictionary for each user and add it to the list
            user_dict = {'username': username, 'password': password}
            credentials.append(user_dict)

    return credentials


def get_auth(user_nr=0, password_path='../auth.tsv'):
    credentials = read_credentials(password_path)
    user = credentials[user_nr]
    auth = HTTPBasicAuth(user['username'], user['password'])
    return auth

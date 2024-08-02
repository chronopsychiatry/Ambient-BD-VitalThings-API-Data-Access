
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import logging
import configparser

from download.data_download import DataDownloader
from authentication.file_auth import SimpleFileAuth
from sf_api.somnofy import *
from storage.paths_resolver import PathsResolver


class Properties():
    def __init__(self, auth_file = '../auth.tsv', auth_user = 0,
                 download_folder = '../downloaded_data', from_date = None):
        self.auth_file = auth_file
        self.auth_user = auth_user
        self.download_folder = download_folder
        if from_date is None:
            from_date = datetime.datetime.now() - datetime.timedelta(days=14)
        # if from_date is a string, convert it to datetime
        if isinstance(from_date, str):
            from_date = datetime.datetime.fromisoformat(from_date)
        self.from_date = from_date



def load_application_properties():
    config = configparser.ConfigParser()
    config.read('application.properties')
    return Properties(
        auth_file=config['DEFAULT']['auth-file'],
        auth_user=int(config['DEFAULT']['auth-user']),
        download_folder=config['DEFAULT']['download-dir'],
        from_date= config['DEFAULT']['from-date']
    )

def user_to_subject_id(user):
    return user.last_name+'-'+user.id

def main():
    # Configure the logger
    logging.basicConfig(
        level=logging.INFO,  # Set the log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[
            logging.FileHandler("download.log"),  # Log to a file
            logging.StreamHandler()  # Log to console
        ]
    )

    logger = logging.getLogger('main')

    properties = load_application_properties()

    authentication = SimpleFileAuth(properties.auth_file)
    auth = authentication.get_auth(properties.auth_user)
    from_date = properties.from_date

    logger.info("Accessing somnofy with user: {}".format(auth.username))

    somnofy = Somnofy(auth)


    users = somnofy.get_users()
    for u in users:
        logger.info(f"{u}")

    resolver = PathsResolver(properties.download_folder)
    downloader = DataDownloader(somnofy, resolver=resolver)

    for u in users:
        downloader.save_user_data(user_to_subject_id(u), from_date)

    '''
    
    user_id = '6675947f056bcf001afae435'
    sessions = somnofy.get_all_sessions_for_user(user_id, from_date = '2024-07-20T22:22:42.739001')
    for s in sessions:
        print(s)    
    # lorna
    user_id = '64d22532c58c030014afb890'

    # tomek
    user_id = '65367bfb2b751b0013e9bebf'

'''


if __name__ == '__main__':
    main()
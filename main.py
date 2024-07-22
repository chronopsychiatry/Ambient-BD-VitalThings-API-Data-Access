
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import logging

from download.data_download import DataDownloader
from authentication.file_auth import SimpleFileAuth
from sf_api.somnofy import *




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


    authentication = SimpleFileAuth()
    auth = authentication.get_auth(1)

    logger.info("Accessing somnofy with user: {}".format(auth.username))

    from_date = (datetime.datetime.now() - datetime.timedelta(days=30))
    somnofy = Somnofy(auth)


    users = somnofy.get_users()
    for u in users:
        logger.info(f"Available {u}")

    downloader = DataDownloader(somnofy)

    for u in users:
        downloader.save_user_data(u.id, from_date)

'''
    # lorna
    user_id = '64d22532c58c030014afb890'

    # tomek
    user_id = '65367bfb2b751b0013e9bebf'

'''


if __name__ == '__main__':
    main()
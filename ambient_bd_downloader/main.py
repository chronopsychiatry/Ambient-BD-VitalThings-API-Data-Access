import datetime
import logging
import configparser
from typing import Union

from ambient_bd_downloader.download.data_download import DataDownloader
from ambient_bd_downloader.authentication.file_auth import SimpleFileAuth
from ambient_bd_downloader.sf_api.somnofy import Somnofy
from ambient_bd_downloader.storage.paths_resolver import PathsResolver


class Properties():
    def __init__(self, auth_file=None,
                 auth_user: Union[str, int] = None,
                 download_folder='../downloaded_data',
                 from_date=None,
                 ignore_epoch_for_shorter_than_hours: Union[str, float] = None,
                 flag_nights_with_sleep_under_hours: Union[str, float] = None):

        self.auth_file = auth_file or './auth.tsv'
        self.auth_user = int(auth_user or 0)
        self.download_folder = download_folder or '../downloaded_data'

        if from_date is None:
            from_date = datetime.datetime.now() - datetime.timedelta(days=14)
        # if from_date is a string, convert it to datetime
        if isinstance(from_date, str):
            from_date = datetime.datetime.fromisoformat(from_date)
        self.from_date = from_date

        self.ignore_epoch_for_shorter_than_hours = float(ignore_epoch_for_shorter_than_hours or 2)
        self.flag_nights_with_sleep_under_hours = float(flag_nights_with_sleep_under_hours or 5)

    def __str__(self):
        return f"Properties(auth_file={self.auth_file}, auth_user={self.auth_user}, " \
               f"download_folder={self.download_folder}, from_date={self.from_date}, " \
               f"ignore_epoch_for_shorter_than_hours={self.ignore_epoch_for_shorter_than_hours}, " \
               f"flag_nights_with_sleep_under_hours={self.flag_nights_with_sleep_under_hours})"


def load_application_properties():
    config = configparser.ConfigParser()
    config.read('application.properties')
    return Properties(
        auth_file=config['DEFAULT'].get('auth-file', None),
        auth_user=config['DEFAULT'].get('auth-user', None),
        download_folder=config['DEFAULT'].get('download-dir', None),
        from_date=config['DEFAULT'].get('from-date', None),
        ignore_epoch_for_shorter_than_hours=config['DEFAULT'].get('ignore-epoch-for-shorter-than-hours', None),
        flag_nights_with_sleep_under_hours=config['DEFAULT'].get('flag-nights-with-sleep-under-hours', None)
    )


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
    logger.info(f"Properties: {properties}")

    authentication = SimpleFileAuth(properties.auth_file)
    auth = authentication.get_auth(properties.auth_user)
    from_date = properties.from_date

    logger.info("Accessing somnofy with user: {}".format(auth.username))

    somnofy = Somnofy(auth)

    users = somnofy.get_users()
    for u in users:
        logger.info(f"{u}")

    resolver = PathsResolver(properties.download_folder)
    downloader = DataDownloader(somnofy, resolver=resolver,
                                ignore_epoch_for_shorter_than_hours=properties.ignore_epoch_for_shorter_than_hours,
                                filter_shorter_than_hours=properties.flag_nights_with_sleep_under_hours)

    for u in users:
        downloader.save_user_data(u, from_date)


if __name__ == '__main__':
    main()

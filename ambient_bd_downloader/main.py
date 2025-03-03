import datetime
import logging
import configparser
from typing import Union
import os

from ambient_bd_downloader.download.data_download import DataDownloader
from ambient_bd_downloader.sf_api.somnofy import Somnofy
from ambient_bd_downloader.storage.paths_resolver import PathsResolver


class Properties():
    def __init__(self, client_id_file=None,
                 zone_name=None,
                 download_folder='../downloaded_data',
                 from_date=None,
                 ignore_epoch_for_shorter_than_hours: Union[str, float] = None,
                 flag_nights_with_sleep_under_hours: Union[str, float] = None):

        self.client_id_file = client_id_file or './client_id.txt'
        self.zone_name = zone_name
        self.download_folder = download_folder or '../downloaded_data'
        with open(client_id_file, 'r') as f:
            self.client_id = f.readline().strip(' \t\n\r')

        if from_date is None:
            from_date = datetime.datetime.now() - datetime.timedelta(days=14)
        # if from_date is a string, convert it to datetime
        if isinstance(from_date, str):
            from_date = datetime.datetime.fromisoformat(from_date)
        self.from_date = from_date

        self.ignore_epoch_for_shorter_than_hours = float(ignore_epoch_for_shorter_than_hours or 2)
        self.flag_nights_with_sleep_under_hours = float(flag_nights_with_sleep_under_hours or 5)

    def __str__(self):
        return f"Properties(client_id_file={self.client_id_file}, " \
               f"zone_name={self.zone_name}, " \
               f"download_folder={self.download_folder}, from_date={self.from_date}, " \
               f"ignore_epoch_for_shorter_than_hours={self.ignore_epoch_for_shorter_than_hours}, " \
               f"flag_nights_with_sleep_under_hours={self.flag_nights_with_sleep_under_hours})"


def load_application_properties(file_path='./ambient_downloader.properties'):
    config = configparser.ConfigParser()
    if os.path.exists(file_path):
        config.read(file_path)
    else:
        raise ValueError(f"Properties file not found: {file_path}. Run generate_config to create it.")
    return Properties(
        client_id_file=config['DEFAULT'].get('client-id-file', None),
        zone_name=config['DEFAULT'].get('zone', None),
        download_folder=config['DEFAULT'].get('download-dir', None),
        from_date=config['DEFAULT'].get('from-date', None),
        ignore_epoch_for_shorter_than_hours=config['DEFAULT'].get('ignore-epoch-for-shorter-than-hours', None),
        flag_nights_with_sleep_under_hours=config['DEFAULT'].get('flag-nights-with-sleep-under-hours', None)
    )


def main():
    properties = load_application_properties()

    # Configure the logger
    if not os.path.exists(properties.download_folder):
        os.makedirs(properties.download_folder)
    logging.basicConfig(
        level=logging.INFO,  # Set the log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[
            logging.FileHandler(os.path.join(properties.download_folder, "download.log")),  # Log to a file
            logging.StreamHandler()  # Log to console
        ]
    )

    logger = logging.getLogger('main')
    logger.info(f"Properties: {properties}")

    from_date = properties.from_date

    logger.info(f'Accessing somnofy zone "{properties.zone_name}"'
                f' with client ID stored at: {properties.client_id_file}')

    somnofy = Somnofy(properties)

    if not somnofy.has_zone_access():
        raise ValueError(f'Access to zone "{properties.zone_name}" denied.')
    subjects = somnofy.get_subjects()
    for u in subjects:
        logger.info(f"{u}")

    resolver = PathsResolver(os.path.join(properties.download_folder, properties.zone_name))
    downloader = DataDownloader(somnofy, resolver=resolver,
                                ignore_epoch_for_shorter_than_hours=properties.ignore_epoch_for_shorter_than_hours,
                                filter_shorter_than_hours=properties.flag_nights_with_sleep_under_hours)

    for u in subjects:
        downloader.save_subject_data(u, from_date)


if __name__ == '__main__':
    main()

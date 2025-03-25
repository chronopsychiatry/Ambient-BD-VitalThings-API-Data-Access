import os
import logging
import pkg_resources

from ambient_bd_downloader.sf_api.somnofy import Somnofy
from ambient_bd_downloader.sf_api.dom import get_subject_by_id
from ambient_bd_downloader.properties.properties import load_application_properties


def check_devices():
    properties = load_application_properties()

    # Configure the logger
    if not os.path.exists(properties.device_check_folder):
        os.makedirs(properties.device_check_folder)
    logging.basicConfig(
        level=logging.INFO,  # Set the log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
        handlers=[
            logging.FileHandler(os.path.join(properties.device_check_folder, "device_check.log")),  # Log to a file
            logging.StreamHandler()  # Log to console
        ]
    )

    logger = logging.getLogger('device_check')
    version = pkg_resources.require("ambient-bd-downloader")[0].version
    logger.info(f'Running ambient_bd_downloader version {version}')
    logger.info(f'Properties: {properties}')

    logger.info(f'Accessing somnofy zone "{properties.zone_name}"'
                f' with client ID stored at: {properties.client_id_file}')

    somnofy = Somnofy(properties)

    if not somnofy.has_zone_access():
        raise ValueError(f'Access to zone "{properties.zone_name}" denied.')

    devices = somnofy.get_devices()
    subjects = somnofy.get_subjects()

    for d in devices:
        subject = get_subject_by_id(subjects, d.subject_id)
        print(subject)
        status = "online" if d.online else "offline"
        logger.info(f"Device {d.name} of subject {subject.identifier} is {status}. "
                    f"Latest connection on {d.latest_connection}")


import os
import logging

class PathsResolver:

    def __init__(self, path = os.path.join('..', 'downloaded_data')):
        self._logger = logging.getLogger(__name__)
        self._main_dir = None
        self.set_main_dir(path)

    def set_main_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.isdir(path):
            raise ValueError(f'Main storage: {path} is not a directory')
        self._main_dir = path
        self._logger.info(f'Using storage dir: {os.path.abspath(self._main_dir)}')

    def get_main_dir(self):
        return self._main_dir

    def get_user_dir(self, user_id):
        user_dir = os.path.join(self._main_dir, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir

    def get_user_sys_dir(self, user_id):
        sys_dir = os.path.join(self.get_user_dir(user_id), 'sys')
        if not os.path.exists(sys_dir):
            os.makedirs(sys_dir)
        return sys_dir

    def get_user_data_dir(self, user_id):
        data_dir = os.path.join(self.get_user_dir(user_id), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir

    def get_user_raw_dir(self, user_id):
        raw_dir = os.path.join(self.get_user_dir(user_id), 'raw')
        if not os.path.exists(raw_dir):
            os.makedirs(raw_dir)
        return raw_dir

    def get_user_last_session(self, user_id):
        return os.path.join(self.get_user_sys_dir(user_id), 'last_session.json')

    def has_last_session(self, user_id):
        last_path = os.path.join(self._main_dir, user_id, 'sys', 'last_session.json')
        return os.path.exists(last_path)


    def get_user_global_report(self, user_id):
        return os.path.join(self.get_user_data_dir(user_id), 'all_sessions_report.csv')


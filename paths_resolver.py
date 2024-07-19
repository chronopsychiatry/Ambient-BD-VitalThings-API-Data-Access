import datetime
import os

class PathsResolver:

    def __init__(self, path = os.path.join('.','downloaded_data')):

        self.main_dir = path

    # define instance method set_main_dir
    def set_main_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.isdir(path):
            raise ValueError(f'Main storage: {path} is not a directory')
        self.main_dir = path

    def get_main_dir(self):
        return self.main_dir

    def get_user_dir(self, user_id):
        user_dir = os.path.join(self.main_dir, user_id)
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
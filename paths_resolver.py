import datetime
import os

class PathsResolver:

    def __init__(self, path = './data'):

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
        return os.path.join(self.main_dir, user_id)

    def get_user_sys_dir(self, user_id):
        return os.path.join(self.get_user_dir(user_id), 'sys')

    def get_user_data_dir(self, user_id):
        return os.path.join(self.get_user_dir(user_id), 'data')

    def get_user_raw_dir(self, user_id):
        return os.path.join(self.get_user_dir(user_id), 'raw')

    def get_user_last_session(self, user_id):
        return os.path.join(self.get_user_sys_dir(user_id), 'last_session.json')
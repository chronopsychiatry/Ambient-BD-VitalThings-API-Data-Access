import tempfile
import os
import pytest
from ambient_bd_downloader.storage.paths_resolver import PathsResolver


class TestPathsResolver():

    temp_dir = tempfile.TemporaryDirectory()
    test_dir = temp_dir.name
    resolver = PathsResolver(test_dir)

    def test_initialization(self):
        assert self.resolver._main_dir == self.test_dir

    def test_set_main_dir_creates_directory(self):
        test_main_dir = os.path.join(self.test_dir, 'main')
        resolver = PathsResolver()
        resolver.set_main_dir(test_main_dir)
        assert os.path.exists(test_main_dir)
        assert resolver.get_main_dir() == test_main_dir

    def test_set_main_dir_raises_exception(self):
        path = os.path.join(self.test_dir, 'file.txt')
        with open(path, 'w') as temp_file:
            temp_file.write('This is a temporary file.')
        with pytest.raises(ValueError):
            self.resolver.set_main_dir(path)

    def test_get_subject_dir(self):
        expected_path = os.path.join(self.test_dir, 'subject1')
        assert self.resolver.get_subject_dir('subject1') == expected_path

    def test_get_subject_sys_dir(self):
        expected_path = os.path.join(self.test_dir, 'subject1', 'sys')
        assert self.resolver.get_subject_sys_dir('subject1') == expected_path

    def test_get_subject_data_dir(self):
        expected_path = os.path.join(self.test_dir, 'subject1', 'data')
        assert self.resolver.get_subject_data_dir('subject1') == expected_path

    def test_get_subject_raw_dir(self):
        expected_path = os.path.join(self.test_dir, 'subject1', 'raw')
        assert self.resolver.get_subject_raw_dir('subject1') == expected_path

    def test_get_subject_last_session(self):
        expected_path = os.path.join(self.test_dir, 'subject1', 'sys', 'last_session.json')
        assert self.resolver.get_subject_last_session('subject1') == expected_path

    def test_get_subject_global_report(self):
        expected_path = os.path.join(self.test_dir, 'subject1', 'data', 'all_sessions_report.csv')
        assert self.resolver.get_subject_global_report('subject1') == expected_path

    def test_tearDown(self):
        self.temp_dir.cleanup()

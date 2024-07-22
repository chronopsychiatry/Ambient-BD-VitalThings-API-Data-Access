import unittest
import tempfile
import os
from storage.paths_resolver import PathsResolver

class TestPathsResolver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name
        self.resolver = PathsResolver(self.test_dir)

    def test_initialization(self):
        self.assertEqual(self.resolver._main_dir, self.test_dir)

    def test_set_main_dir_creates_directory(self):
        test_main_dir = os.path.join(self.test_dir, 'main')
        self.resolver.set_main_dir(test_main_dir)
        self.assertTrue(os.path.exists(test_main_dir))
        self.assertEqual(self.resolver.get_main_dir(), test_main_dir)

    def test_set_main_dir_raises_exception(self):
        path = os.path.join(self.test_dir, 'file.txt')
        with open(path, 'w') as temp_file:
            temp_file.write('This is a temporary file.')
        with self.assertRaises(ValueError):
            self.resolver.set_main_dir(path)

    def test_get_user_dir(self):
        #self.resolver.set_main_dir(self.test_dir)
        expected_path = os.path.join(self.test_dir, 'user1')
        self.assertEqual(self.resolver.get_user_dir('user1'), expected_path)

    def test_get_user_sys_dir(self):
        #self.resolver.set_main_dir(self.test_dir)
        expected_path = os.path.join(self.test_dir, 'user1', 'sys')
        self.assertEqual(self.resolver.get_user_sys_dir('user1'), expected_path)

    def test_get_user_data_dir(self):
        #self.resolver.set_main_dir(self.test_dir)
        expected_path = os.path.join(self.test_dir, 'user1', 'data')
        self.assertEqual(self.resolver.get_user_data_dir('user1'), expected_path)

    def test_get_user_raw_dir(self):
        #self.resolver.set_main_dir(self.test_dir)
        expected_path = os.path.join(self.test_dir, 'user1', 'raw')
        self.assertEqual(self.resolver.get_user_raw_dir('user1'), expected_path)

    def test_get_user_last_session(self):
        #self.resolver.set_main_dir(self.test_dir)
        expected_path = os.path.join(self.test_dir, 'user1', 'sys', 'last_session.json')
        self.assertEqual(self.resolver.get_user_last_session('user1'), expected_path)

    def tearDown(self):
        self.temp_dir.cleanup()

if __name__ == '__main__':
    unittest.main()
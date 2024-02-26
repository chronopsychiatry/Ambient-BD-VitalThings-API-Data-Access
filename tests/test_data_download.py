import os
import tempfile
import unittest
from unittest import TestCase

from data_download import set_out_dir, get_out_dir


class Test(TestCase):
    def test_set_out_dir(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set the path to the temporary directory child 'data'
            path = os.path.join(temp_dir, 'data')

            set_out_dir(path)
            self.assertEqual(get_out_dir(), path)

            self.assertTrue(os.path.exists(path))

            # Test if ValueError is raised when set_out_dir is called with a file path

            path = os.path.join(temp_dir, 'file.txt')
            with open(path, 'w') as temp_file:
                temp_file.write('This is a temporary file.')

            with self.assertRaises(ValueError):
                set_out_dir(path)


if __name__ == '__main__':
    unittest.main()

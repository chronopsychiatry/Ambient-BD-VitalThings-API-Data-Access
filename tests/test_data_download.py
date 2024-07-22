import json
import os
import tempfile
import unittest
import datetime

from download.data_download import DataDownloader
from sf_api.dom import Session
from sf_api.somnofy import Somnofy, SESSION_DATA_OUTPUTS
from storage.paths_resolver import PathsResolver


# make class TestSomnofy subclass of Somnofy
class MockSomnofy(Somnofy):

    # define method __init__
    def __init__(self):
        self.test_session_json = os.path.join('data','2024-07-20_VFNPVRgHFAA1AwAA_raw.json')
        print(f'session_json: {os.path.abspath(self.test_session_json)}')

    def _read_test_session_json(self):
        with open(self.test_session_json, 'r') as f:
            return json.load(f)

    # define method get_users
    def get_users(self):
        # return list of dictionaries
        return [{'id': '1'}, {'id': '2'}, {'id': '3'}]


    def get_all_sessions_for_user(self, user_id, from_date=None, to_date=None):
        session = Session(self._read_test_session_json())
        # return list of dictionaries
        return [session]

    def get_session_json(self, session_id, user_id, embeds = SESSION_DATA_OUTPUTS):
        session = self._read_test_session_json()
        session['session_id'] = session_id
        session['user_id'] = user_id;
        return session


class TestDataDownloader(unittest.TestCase):

    def setUp(self):
        self.mock_somnofy = MockSomnofy()
        self.test_dir = tempfile.TemporaryDirectory()
        self.mock_resolver = PathsResolver(path = self.test_dir.name)
        self.data_downloader = DataDownloader(somnofy=self.mock_somnofy, resolver=self.mock_resolver)

    def test_init_without_somnofy_raises_error(self):
        with self.assertRaises(ValueError):
            DataDownloader(somnofy=None, resolver=self.mock_resolver)

    def test_save_user_data(self):

        user_id = 'test_user'
        self.data_downloader.save_user_data(user_id,start_date = datetime.datetime.now() - datetime.timedelta(days=1))

        s_json = self.mock_somnofy._read_test_session_json()
        session_id = s_json["session_id"]
        session = Session(s_json)
        dates = self.data_downloader._sessions_to_date_range(session, session)

        # check if raw data was saved
        raw_data_file = self.data_downloader._raw_session_file(s_json, user_id, session_id)
        self.assertTrue(os.path.isfile(raw_data_file))

        # check if epoch data was saved
        epoch_data_file = self.data_downloader._epoch_data_file(user_id, dates)
        self.assertTrue(os.path.isfile(epoch_data_file))

        # check if reports were saved
        reports_file = self.data_downloader._reports_file(user_id, dates)
        self.assertTrue(os.path.isfile(reports_file))

        # check if last session was saved
        last_session_file = self.mock_resolver.get_user_last_session(user_id)
        self.assertTrue(os.path.isfile(last_session_file))

        # check if compliance data was saved
        compliance_file = self.data_downloader._compliance_file(user_id, dates)
        self.assertTrue(os.path.isfile(compliance_file))


    def test_session_to_date_range(self):
        s_json = self.mock_somnofy._read_test_session_json()
        s_json['start_time'] = '2024-07-20T22:00:00'
        s_session = Session(s_json)
        e_json = self.mock_somnofy._read_test_session_json()
        e_json['end_time'] = '2024-07-21T06:00:00'
        e_session = Session(e_json)

        start_date, end_date = self.data_downloader._sessions_to_date_range(s_session, e_session)
        self.assertEqual(start_date, datetime.date.fromisoformat('2024-07-20'))
        self.assertEqual(end_date, datetime.date.fromisoformat('2024-07-21'))



    def test_calculate_start_date_with_no_date(self):
        with self.assertRaises(ValueError):
            self.data_downloader.calculate_start_date(user_id='test_user')

        proposed_date = '2020-01-01'
        self.assertEqual(self.data_downloader.calculate_start_date(user_id='test_user', proposed_date=proposed_date), proposed_date)

        last_session_file = self.mock_resolver.get_user_last_session(user_id='test_user')
        last_session = {'end_time': '2023-01-01T00:00:00'}
        try:
            with open(last_session_file, 'w') as f:
                json.dump(last_session, f)
            # print(f'last_session_file: {os.path.abspath(last_session_file)}')

            last_session['end_time'] = datetime.datetime.fromisoformat(last_session['end_time'])
            self.assertEqual(self.data_downloader.calculate_start_date(user_id='test_user', proposed_date=proposed_date, force_saved_date=True), last_session['end_time'])
        finally:
            os.remove(last_session_file)
            pass

    def tearDown(self):
        self.test_dir.cleanup()

if __name__ == '__main__':
    unittest.main()





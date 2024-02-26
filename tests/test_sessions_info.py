import unittest
from datetime import datetime
from unittest import TestCase

import pandas as pd

from sessions_info import group_sessions_by_enddate, calculate_aggregated_sessions_stats, make_data_frame_from_session
from sf_api.dom import Session, date_from_iso_string

test_sessions = [
            Session({
                'session_id': '1',
                'device_serial_number': '1',
                'state': 'ENDED',
                'user_id': '2',
                'start_time': '2023-08-01T00:00:00Z',
                'end_time': '2023-08-01T01:00:00Z',
            }),
            Session({
                'session_id': '2',
                'device_serial_number': '1',
                'state': 'ENDED',
                'user_id': '2',
                'start_time': '2023-08-02T00:00:00Z',
                'end_time': '2023-08-02T01:00:00Z',
            }),
            Session({
                'session_id': '3',
                'device_serial_number': '1',
                'state': 'ENDED',
                'user_id': '2',
                'start_time': '2023-08-03T00:30:00Z',
                'end_time': '2023-08-03T01:00:00Z'
            }),
            Session({
                'session_id': '4',
                'device_serial_number': '1',
                'state': 'ENDED',
                'user_id': '2',
                'start_time': '2023-08-01T02:00:00Z',
                'end_time': '2023-08-01T04:00:00Z'
            }),

]



class Test(TestCase):
    def test_group_sessions_by_enddate(self):

        result = group_sessions_by_enddate(test_sessions)

        print(result)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[date_from_iso_string('2023-08-01')]), 2)
        self.assertEqual(len(result[date_from_iso_string('2023-08-02')]), 1)
        self.assertEqual(len(result[date_from_iso_string('2023-08-03')]), 1)
        self.assertIsNone(result.get(date_from_iso_string('2023-08-07')))


    def test_aggregated_sessions_stats(self):

        groups = group_sessions_by_enddate(test_sessions)
        result = calculate_aggregated_sessions_stats(groups)
        print(result)

        # Expected result
        expected_result = {
            datetime(2023, 8, 1).date(): {
                'total_duration': 3*3600.0, 'num_sessions': 2, 'max_duration': 2*3600.0,
                'device_serial_number': '1', 'user_id': '2'
            },
            datetime(2023, 8, 2).date(): {'total_duration': 3600.0, 'num_sessions': 1, 'max_duration': 3600.0,
                'device_serial_number': '1', 'user_id': '2'
            },
            datetime(2023, 8, 3).date(): {'total_duration': 1800.0, 'num_sessions': 1, 'max_duration': 1800.0,
                'device_serial_number': '1', 'user_id': '2'
            },
        }

        self.assertEqual(result, expected_result)

    def test_make_data_frame_from_session(self):
        # Create a mock session JSON object
        session_json = {
            '_embedded': {
                'sleep_analysis': {
                    'epoch_data': [{'movement_mean': 7.17,'time_offset': 0}],
                    'hypnogram': [{'sleep_stage':4,  'timestamp': '2024-02-20T00:01:16.990000'}]
                }
            }
        }

        # Call the function with the mock object
        df = make_data_frame_from_session(session_json)

        # Assert that the returned DataFrame has the expected structure
        expected_df = pd.DataFrame({
            'timestamp': ['2024-02-20T00:01:16.990000'],
            'sleep_stage': [4],
            'movement_mean': [7.17],
            'time_offset': [0]
        })
        pd.testing.assert_frame_equal(df, expected_df)

if __name__ == '__main__':
    unittest.main()
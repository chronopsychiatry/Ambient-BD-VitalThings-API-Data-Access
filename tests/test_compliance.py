import unittest
from unittest import TestCase
from datetime import datetime
from compliance import get_dates_between, build_user_nights_dataframe
import pandas

from sf_api.dom import User


def makeUser(user_id, valid_nights) -> User:
    u = User({'id': user_id, 'created_at' : '2023-08-01T00:00:00Z'})
    u.valid_nights = valid_nights
    return u




class Test(TestCase):
    def test_get_dates_between(self):
        # Test case 1: Dates in range
        start_date = datetime(2023, 1, 1).date()
        end_date = datetime(2023, 1, 5).date()
        expected_result1 = [datetime(2023, 1, 1).date(), datetime(2023, 1, 2).date(),
                            datetime(2023, 1, 3).date(), datetime(2023, 1, 4).date(),
                            datetime(2023, 1, 5).date()]

        result1 = get_dates_between(start_date, end_date)
        self.assertEqual(result1, expected_result1)

        # Test case 2: Dates with only one day
        start_date = datetime(2023, 1, 20).date()
        end_date = datetime(2023, 1, 20).date()
        expected_result3 = [datetime(2023, 1, 20).date()]
        result3 = get_dates_between(start_date, end_date)
        self.assertEqual(result3, expected_result3)

        # Test case 3: Dates wrong starts after end
        start_date = datetime(2023, 1, 20).date()
        end_date = datetime(2023, 1, 10).date()
        expected_result4 = []
        result4 = get_dates_between(start_date, end_date)
        self.assertEqual(result4, expected_result4)

    def test_build_user_nights_dataframe(self):
        # Create sample users_nights dictionary
        users_nights = {
            makeUser(1,2): {
                datetime(2023, 1, 1).date(): {'max_duration': 3600, 'device_serial_number': 'A'},
                datetime(2023, 1, 2).date(): {'max_duration': 7200, 'device_serial_number': 'A'}
            },
            makeUser(2,2): {
                datetime(2023, 1, 1).date(): {'max_duration': 1800, 'device_serial_number': 'B'},
                datetime(2023, 1, 3).date(): {'max_duration': 5400, 'device_serial_number': 'B'}
            }
        }

        # Create sample dates list
        dates = [datetime(2023, 1, 1).date(),
                 datetime(2023, 1, 2).date(),
                 datetime(2023, 1, 3).date()]

        # Expected DataFrame
        expected_df = pandas.DataFrame({
            'user_id': [1, 2],
            'device_serial_number': ['A', 'B'],
            'valid_nights': [2, 2],
            datetime(2023, 1, 1).date(): [3600/3600, 1800/3600],
            datetime(2023, 1, 2).date(): [7200/3600, 'NaN'],
            datetime(2023, 1, 3).date(): ['NaN', 5400/3600]
        })

        # Call the function
        result_df = build_user_nights_dataframe(users_nights, dates)

        print(result_df)
        # Assert that the result matches the expected DataFrame
        pandas.testing.assert_frame_equal(result_df, expected_df)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()

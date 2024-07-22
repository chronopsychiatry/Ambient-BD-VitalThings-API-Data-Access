import unittest
from download.compliance import ComplianceChecker
from datetime import datetime
import pandas as pd

class TestComplianceChecker(unittest.TestCase):
    def setUp(self):
        self.checker = ComplianceChecker()
        self.sample_records = pd.DataFrame({
            'session_id': [1, 2, 3, 4],
            'session_end': ['2023-01-01 08:00:00', '2023-01-01 07:00:00', '2023-01-02 09:00:00', '2023-01-04 06:00:00'],
            'time_asleep': [3600*3, 3600*4, 2.5*3600, 3600*5]
        })
        self.sample_records['session_end'] = pd.to_datetime(self.sample_records['session_end'])

    def test_aggregate_session_records(self):
        result = self.checker.aggregate_session_records(self.sample_records)
        self.assertIn('night_date', result.columns)
        self.assertIn('number_of_long_sessions', result.columns)
        self.assertIn('max_time_asleep_h', result.columns)
        self.assertIn('valid', result.columns)

        expected = pd.DataFrame({
            'night_date': ['2023-01-01', '2023-01-02','2023-01-04'],
            'number_of_long_sessions': [2, 1,  1],
            'max_time_asleep_h': [4.0, 2.5,  5.0],
            'valid': [True, False, True]
        })
        expected['night_date'] = pd.to_datetime(expected['night_date']).dt.date
        self.assertEqual(result.to_dict(), expected.to_dict())

    def test_add_missing_nights(self):
        compliance_info = self.checker.aggregate_session_records(self.sample_records)
        start_date = datetime(2023, 1, 1).date()
        end_date = datetime(2023, 1, 5).date()
        result = self.checker.add_missing_nights(compliance_info, start_date, end_date)
        self.assertEqual(len(result), 5)

        self.assertTrue((result.loc[result['night_date'].isin([datetime(2023, 1, 3).date(), datetime(2023, 1, 5).date()]), 'number_of_long_sessions'] == 0).all())
        self.assertTrue((result.loc[result['night_date'].isin([datetime(2023, 1, 1).date(), datetime(2023, 1, 4).date()]), 'valid'] == True).all())

    def test_calculate_compliance(self):
        dates = [datetime(2023, 1, 1).date(), datetime(2023, 1, 5).date()]
        result = self.checker.calculate_compliance(self.sample_records, dates)
        self.assertEqual(len(result), 5)
        self.assertTrue(result['night_date'].is_monotonic_increasing)

if __name__ == '__main__':
    unittest.main()



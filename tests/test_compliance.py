from ambient_bd_downloader.download.compliance import ComplianceChecker
from datetime import datetime
import pandas as pd


class TestComplianceChecker():

    checker = ComplianceChecker()
    sample_records = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'session_end': ['2023-01-01 08:00:00', '2023-01-01 07:00:00', '2023-01-02 09:00:00', '2023-01-04 06:00:00'],
        'time_in_bed': [3600*4.1, 3600*3.5, 2.6*3600, 3600*5.1],
        'time_asleep': [3600*3, 3600*4, 2.5*3600, 3600*5]
    })
    sample_records['session_end'] = pd.to_datetime(sample_records['session_end'])
    checker.flag_shorter_than_hours = 5

    def test_aggregate_session_records(self):
        result = self.checker.aggregate_session_records(self.sample_records)
        assert 'night_date' in result.columns
        assert 'number_of_long_sessions' in result.columns
        assert 'max_time_asleep_h' in result.columns
        assert 'valid' in result.columns

        expected = pd.DataFrame({
            'night_date': ['2023-01-01', '2023-01-02', '2023-01-04'],
            'number_of_long_sessions': [2, 1,  1],
            'max_time_in_bed_h': [4.1, 2.6, 5.1],
            'max_time_asleep_h': [4.0, 2.5,  5.0],
            'total_sleep_time_h': [7.0, 2.5, 5.0],
            'valid': [True, False, True]
        })
        expected['night_date'] = pd.to_datetime(expected['night_date']).dt.date
        assert result.equals(expected)

    def test_uses_flag_parameter_to_mark_valid(self):
        self.checker.flag_shorter_than_hours = 3
        result = self.checker.aggregate_session_records(self.sample_records)
        date = datetime(2023, 1, 2).date()  # noqa: F841
        assert not result.query('night_date == @date')['valid'].all()

        self.checker.flag_shorter_than_hours = 2.5
        result = self.checker.aggregate_session_records(self.sample_records)
        assert result.query('night_date == @date')['valid'].all()

    def test_add_missing_nights(self):
        compliance_info = self.checker.aggregate_session_records(self.sample_records)
        start_date = datetime(2023, 1, 1).date()
        end_date = datetime(2023, 1, 5).date()
        result = self.checker.add_missing_nights(compliance_info, start_date, end_date)
        assert len(result) == 5

        dates_no_nights = [datetime(2023, 1, 3).date(), datetime(2023, 1, 5).date()]  # noqa: F841
        assert not result.query('night_date in @dates_no_nights')['number_of_long_sessions'].all()
        dates_valid = [datetime(2023, 1, 1).date(), datetime(2023, 1, 4).date()]  # noqa: F841
        assert result.query('night_date in @dates_valid')['valid'].all()

    def test_calculate_compliance(self):
        dates = [datetime(2023, 1, 1).date(), datetime(2023, 1, 5).date()]
        result = self.checker.calculate_compliance(self.sample_records, dates)
        assert len(result) == 5
        assert result['night_date'].is_monotonic_increasing

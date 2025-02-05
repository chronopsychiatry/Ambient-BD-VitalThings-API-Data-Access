import datetime
import json
import os
import pandas as pd
import logging

from ambient_bd_downloader.sf_api.dom import Subject, Session
from ambient_bd_downloader.download.compliance import ComplianceChecker
from ambient_bd_downloader.storage.paths_resolver import PathsResolver
from ambient_bd_downloader.sf_api.somnofy import Somnofy


class DataDownloader:
    def __init__(self, somnofy: Somnofy, resolver: PathsResolver = None,
                 compliance=ComplianceChecker(),
                 ignore_epoch_for_shorter_than_hours=2,
                 filter_shorter_than_hours=5):
        if not somnofy:
            raise ValueError('Somnofy connection must be provided')
        self._somnofy = somnofy
        if not resolver:
            resolver = PathsResolver()
        self._resolver = resolver
        self._compliance_checker = compliance
        self._compliance_checker.flag_shorter_than_hours = filter_shorter_than_hours
        self.ignore_epoch_for_shorter_than_hours = ignore_epoch_for_shorter_than_hours
        self._logger = logging.getLogger(__name__)

    def get_subject_identity(self, subject):
        return subject.identifier + '-' + subject.id

    def save_subject_data(self, subject: Subject, start_date=None, force_saved_date=True):

        subject_identity = self.get_subject_identity(subject)
        self._logger.info(f'{subject}')
        start_date = self.calculate_start_date(subject_identity, start_date, force_saved_date)
        self._logger.info(f'Downloading data for subject {subject_identity} starting from {start_date}')
        sessions = self._somnofy.get_all_sessions_for_subject(subject.id, start_date)

        if len(sessions) == 0:
            self._logger.info(f'No sessions found for subject {subject_identity} between {start_date} and now')
            return None

        self._logger.info(f'Found {len(sessions)} sessions for subject {subject_identity} between {start_date} and now')

        reports = pd.DataFrame()
        epoch_data = pd.DataFrame()
        last_session = None
        last_session_json = None

        for s in sessions:
            if self._is_in_progress(s, subject_identity):
                continue

            self._logger.info(f'Downloading session {s.session_id} for subject {subject_identity}')

            s_json = self._somnofy.get_session_json(s.session_id)
            self.save_raw_session_data(s_json, subject_identity, s.session_id)

            reports = pd.concat([reports, self._make_session_report(s_json)], ignore_index=True)

            if self._should_store_epoch_data(s):
                epoch_data = pd.concat([epoch_data, self.make_epoch_data_frame_from_session(s_json)], ignore_index=True)

            last_session = s
            last_session_json = s_json

        if len(sessions) == 0:
            return
        if not last_session or not last_session.session_end:
            return
        dates = self._sessions_to_date_range(sessions[0], last_session)

        self.save_reports(reports, subject_identity, dates)
        self.append_to_global_reports(reports, subject_identity)
        self.save_epoch_data(epoch_data, subject_identity, dates)
        compliance_info = self._compliance_checker.calculate_compliance(reports, dates)
        self.save_compliance_info(compliance_info, subject_identity, dates)
        self.save_last_session(last_session_json, subject_identity)

    def _should_store_epoch_data(self, session: Session):
        return (not self.ignore_epoch_for_shorter_than_hours or
                (session.duration_seconds and
                 session.duration_seconds >= self.ignore_epoch_for_shorter_than_hours * 60 * 60))

    def _make_session_report(self, s_json):
        json = s_json['data'].copy()
        json.pop('epoch_data', None)
        df = pd.DataFrame(pd.json_normalize(json))
        return df

    def _is_in_progress(self, session, subject_id):
        if session.state == 'IN_PROGRESS':
            self._logger.debug(f'Skipping session {session.session_id} for subject {subject_id} as it is in progress')
            return True
        return False

    def calculate_start_date(self, subject_id, proposed_date=None, force_saved_date=True):

        if force_saved_date:
            start_date = self._get_date_from_last_session(subject_id) or proposed_date
        else:
            start_date = proposed_date or self._get_date_from_last_session(subject_id)

        if not start_date:
            raise ValueError(f'No start date found for subject {subject_id} and none proposed')

        return start_date

    def _get_date_from_last_session(self, subject_id):
        if not self._resolver.has_last_session(subject_id):
            return None

        session_file = self._resolver.get_subject_last_session(subject_id)
        with open(session_file, 'r') as f:
            session = json.load(f)
            session_end = datetime.datetime.fromisoformat(session['data']['session_end'])
            session_start = datetime.datetime.fromisoformat(session['data']['session_start'])
            # some sessions have duration of 0 and are being re-downloaded even if saved as last session
            # we add one microsecond to end time to avoid re-downloading
            if session_end == session_start:
                session_end = session_end + datetime.timedelta(microseconds=1)
            return session_end

    def save_raw_session_data(self, s_json, subject_id, session_id):

        with open(self._raw_session_file(s_json, subject_id, session_id), 'w') as f:
            json.dump(s_json, f)

    def _raw_session_file(self, s_json, subject_id, session_id):
        start_date = datetime.datetime.fromisoformat(s_json['data']['session_start']).date()
        return os.path.join(self._resolver.get_subject_raw_dir(subject_id), f'{start_date}_{session_id}_raw.json')

    def save_last_session(self, last_session_json, subject_id):
        if last_session_json:
            path = self._resolver.get_subject_last_session(subject_id)
            with open(path, 'w') as f:
                json.dump(last_session_json, f)

    def save_reports(self, reports, subject_id, dates):
        path = self._reports_file(subject_id, dates)
        reports.to_csv(path, index=False)

    def _reports_file(self, subject_id, dates):
        return os.path.join(self._resolver.get_subject_data_dir(subject_id),
                            f'{dates[0]}_{dates[1]}_sessions_reports.csv')

    def _sessions_to_date_range(self, first_session, last_session):
        start_date = first_session.session_start.date()
        end_date = last_session.session_end.date()
        return start_date, end_date

    def save_epoch_data(self, epoch_data, subject_id, dates):
        epoch_data.to_csv(self._epoch_data_file(subject_id, dates), index=False)

    def _epoch_data_file(self, subject_id, dates):
        return os.path.join(self._resolver.get_subject_data_dir(subject_id),
                            f'{dates[0]}_{dates[1]}_epoch_data.csv')

    def make_epoch_data_frame_from_session(self, session_json: dict) -> pd.DataFrame:
        epoch_data = pd.DataFrame(session_json['data']['epoch_data'])
        # epoch_hypnogram = pd.DataFrame(session_json['data']['sleep_analysis']['hypnogram'])

        # check if both has same number of rows, throw exception when not met with actual numbers
        # if len(epoch_data) != len(epoch_hypnogram):
        #     raise Exception(
        #         f"Epoch data and hypnogram data have different number of rows:\
        #             {len(epoch_data)} vs {len(epoch_hypnogram)}")

        # session_data = pd.concat([epoch_hypnogram, epoch_data], axis=1)
        session_data = epoch_data  # Could not find hypnogram data in new API.
# Fix this section when VT have given more details.

        # add session_id as first column
        session_data.insert(0, 'session_id', session_json['data']['id'])

        # change the order of columns that first is 'timestamp' and then rest remains same
        session_data = session_data[['timestamp'] + [col for col in session_data.columns if col != 'timestamp']]
        return session_data

    def append_to_global_reports(self, reports, subject_id):
        file = self._resolver.get_subject_global_report(subject_id)
        reports.to_csv(file, mode='a', header=not os.path.exists(file), index=False)

    def save_compliance_info(self, compliance_info, subject_id, dates):

        path = self._compliance_file(subject_id, dates)
        compliance_info.to_csv(path, index=False)

    def _compliance_file(self, subject_id, dates):
        return os.path.join(self._resolver.get_subject_data_dir(subject_id),
                            f'{dates[0]}_{dates[1]}_compliance_info.csv')

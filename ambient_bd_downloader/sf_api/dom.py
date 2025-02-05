import datetime


def datetime_from_iso_string(string):
    if string.endswith('Z'):
        return datetime.datetime.fromisoformat(string[:-1])
    else:
        return datetime.datetime.fromisoformat(string)


def date_from_iso_string(date_string):
    return datetime.datetime.fromisoformat(date_string).date()


class Session:
    def __init__(self, session_data):
        self.session_id = session_data['id']
        self.device_serial_number = session_data['device_serial_number']
        self.state = session_data['state']
        self.subject_id = session_data['subject_id']

        self.session_start = datetime_from_iso_string(session_data['session_start'])
        if session_data['session_end']:  # end-time not available for in progress sessions
            self.session_end = datetime_from_iso_string(session_data['session_end'])
            # Calculate duration in seconds
            self.duration_seconds = (self.session_end - self.session_start).total_seconds()
        else:
            self.session_end = None
            self.duration_seconds = None

    def __str__(self):
        return f"Session ID: {self.session_id}, Device Serial Number: {self.device_serial_number}, " \
               f"Start Time: {self.session_start}, End Time: {self.session_end}, " \
               f"State: {self.state}, Subject ID: {self.subject_id}, " \
               f"Duration (seconds): {self.duration_seconds}"


class Subject:
    def __init__(self, subject_data):
        self.id = subject_data.get('id')
        self.identifier = subject_data.get('identifier')
        self.sex = subject_data.get('sex')
        self.birth_year = subject_data.get('birth_year')
        self.created_at = datetime_from_iso_string(subject_data.get('created_at'))

    def __str__(self):
        return f"Subject ID: {self.id}, Identifier: {self.identifier}, " \
               f"Sex: {self.sex}, Birth year: {self.birth_year}," \
               f"Created At: {self.created_at}"

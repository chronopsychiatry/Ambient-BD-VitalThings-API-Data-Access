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

        self.start_time = datetime_from_iso_string(session_data['session_start'])
        if session_data['session_end']:  # end-time not available for in progress sessions
            self.end_time = datetime_from_iso_string(session_data['session_end'])
            # Calculate duration in seconds
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        else:
            self.end_time = None
            self.duration_seconds = None

    def __str__(self):
        return f"Session ID: {self.session_id}, Device Serial Number: {self.device_serial_number}, " \
               f"Start Time: {self.start_time}, End Time: {self.end_time}, " \
               f"State: {self.state}, Subject ID: {self.subject_id}, " \
               f"Duration (seconds): {self.duration_seconds}"


class Subject:
    def __init__(self, subject_data):
        self.id = subject_data.get('id')
        self.name = subject_data.get('name')
        self.sex = subject_data.get('sex')
        self.birth_year = subject_data.get('birth_year')
        self.created_at = datetime_from_iso_string(subject_data.get('created_at'))

    def __str__(self):
        return f"Subject ID: {self.id}, Name: {self.name}, " \
               f"Sex: {self.sex}, Birth year: {self.birth_year}," \
               f"Created At: {self.created_at}"

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
        self.session_id = session_data['session_id']
        self.device_serial_number = session_data['device_serial_number']
        self.state = session_data['state']
        self.user_id = session_data['user_id']

        self.start_time = datetime_from_iso_string(session_data['start_time'])
        if session_data['end_time']:  # end-time not available for in progress sessions
            self.end_time = datetime_from_iso_string(session_data['end_time'])
            # Calculate duration in seconds
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        else:
            self.end_time = None
            self.duration_seconds = None

    def __str__(self):
        return f"Session ID: {self.session_id}, Device Serial Number: {self.device_serial_number}, " \
               f"Start Time: {self.start_time}, End Time: {self.end_time}, " \
               f"State: {self.state}, User ID: {self.user_id}, " \
               f"Duration (seconds): {self.duration_seconds}"


class User:
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.display_name = user_data.get('display_name')
        self.gender = user_data.get('gender')
        self.birth_year = user_data.get('birth_year')
        self.created_at = datetime_from_iso_string(user_data['created_at'])

    def __str__(self):
        return f"User ID: {self.id}, Email: {self.email}, First Name: {self.first_name}, " \
               f"Last Name: {self.last_name}, Display Name: {self.display_name}, " \
               f"Gender: {self.gender}, Birth Year: {self.birth_year}, " \
               f"Created At: {self.created_at}"

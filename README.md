# AmbientBD Somnofy data download

This a package for downloading sleep data from the radar devices and storing them in an "analysis friendly" format.

## Installation

### Setting up the environment

We recommend using Anaconda (https://www.anaconda.com/download/) to manage your Python environment. Once you have Anaconda installed, you can create a new environment with the required dependencies by running the following commands:

```conda create -n ambient python=3.12```
    
Activate the environment by running:

```conda activate ambient```
    
Install required dependencies:
- pandas
- requests

by running:

```conda install -c conda-forge pandas requests```

### Installing the package

Clone the repository:

```git clone https://github.com/chronopsychiatry/ambient-somnofy.git```


## Starting the download

To download the data, run the following command:

    Remember to activate the environment before running the command. 
    (conda activate ambient)    

Navigate to the repository:

```
cd ambient-somnofy
python main.py
```

## General behaviours

In the typical use, the program is run periodically (by researcher or automatically) to download the data from the Somnofy server. The program remembers the last downloaded session for each subject and continues the download from there. For each run a new set of output files is generated and marked with the date range of the download (last_session date to current date).

It is recommended to run the program in the afternoon so all the "sleep" sessions will be terminated, as the pgoram ignores the "in progress" sessions.

All raw data are stored in json files as retrieved from Somnofy.

The epoch data are the timeseries of the monitored variables, with time value in the timestamp column. They are called epoch because they contain aggregated data from the 30s epochs.

In the initial cleaning, the short sessions are filtered out from the epoch data. The short sessions are those which are shorter than the specified hours in the `ignore-epoch-for-shorter-than-hours` parameter in the `application.properties` file.

The compliance report is being generated for each night within the download date range. The compliance report contains for example the number of sessions, total sleep time and the flag VALID. The night is considered valid if the total sleep time is greater than the specified hours in the `flag-short-sleep-for-less-than-hours` parameter in the `application.properties` file.

### Monitoring program porgress

The program outputs the current operations or errors to both the console and the log file. 
The log file is stored in the program directory as `download.log`.

## Configuration

All the parameters are stored in `application.properties` file. You can change the parameters in this file to customize the download process.

#### User credentials

Login credentials must be stored in a `.tsv` file which has format:

```
login   password
```

The password file path can be changed in the `application.properties` in `auth_file` parameter. 
Be default it is set to `../auth.tsv`.

> **⚠️ Important Warning:**
> 
> Never store the password file within the program/package folder.
> So it won't be uploaded to the repository by mistake.  
> By default, the password file should be stored in the parent directory of the package folder.
> 

#### Download folder

The download folder can be changed in the `application.properties` in `download_folder` parameter. 
By default, it is set to `downloaded_data` in the parent folder.

Again, it must not be stored within the package folder to prevent upload to the repository

#### Data range

The data range can be changed in the `application.properties` with `from-date` parameter in the ISO format `YYYY-MM-DD`.

Only sessions starting after that date will be downloaded from Somnofy server, so it should be set to the study start date.

As explained in the previous section, the program remembers the last downloaded session (for each study subject ) and continues download from there. Check below for more details how to force the download of all sessions.

#### Filtering and flagging

Somnofy creates a new session everytime  someone enters the room. Those sessions are not useful for the analysis and can be filtered out from the epoch data. The parameter `ignore-epoch-for-shorter-than-hours` can be used to filter out the sessions shorter than the specified hours. These session will not be included in the epoch data but still visible in the session reports.

To help checking the compliance or data capture process, the total hours of sleep are calculated for each night. If the total sleep time is less than the specified hours, the session is flagged as INVALID. The parameter `flag-short-sleep-for-less-than-hours` can be used to set the threshold for the short sleep flag.

#### Multiple users in auth file
Auth file can contain multiple users. The program by default connects with the first credentials in the auth file. But using auth-user parameter in the `application.properties` file, you can specify which user to connect with. The user index starts from 0.

#### Subject ID

Somnofy does not contain researech friendly Subject_ID. It was agreed to use Last Name as the subject_id. 
Actually the program uses the LastName-Somnofy'sUserID as subject id. 
That is because in some test data there was no LastName set and Somnofy'sUserID can be helpful for sanity checks with the server/dashboard.

For example if the user was Tomasz Zielinski, the subject_id could be `Zielinski-66744b82056bcf001afa8d69`.

To change the subject_id, you need to modify the code in the `download/download_data.py` file in the `get_subject_id` function to return the desired user fields combination.


## Data layout and format

Example folder structure for 2 subjects (U03, U04 ) and 2 download program runs
on 2024-07-26 and 2024-08-03. There were no data for subject U03 after 26th July.

```
- downloaded_data
    - U03-66744b82056bcf001afa8d69
        - data
            - 2024-07-14_2024-07-26_epoch_data.csv
            - 2024-07-14_2024-07-26_session_report.csv
            - 2024-07-14_2024-07-26_compliance_info.csv
        - raw
            - 2024-07-14_WUVFRRgHDg4RAgAA.json
            - 2024-07-14_WUVFRRgHDgkCIgAA.json
            - ...
        - sys
            - last_session.json
    - U04-66826ea1056bcf001afdfca1
        - data
            - 2024-07-14_2024-07-26_epoch_data.csv
            - 2024-07-14_2024-07-26_session_report.csv
            - 2024-07-14_2024-07-26_compliance_info.csv
            - 2024-07-27_2024-08-03_epoch_data.csv
            - 2024-07-27_2024-08-03_session_report.csv
            - 2024-07-27_2024-08-03_compliance_info.csv
        - raw
            - 2024-07-15_WUdIQhgHDxYHIgAA.json
            - ...
        - sys
            - last_session.json

```


For each subject a folder is created in the download folder. The folder name is the Subject_ID (as defined above). Inside the subject folder, there are three subfolders: `data` and `raw` and `sys`.

The `sys` folder contains the information used by the program to track the download status. For example it stores the last finished session which has been downloaded. This information is used when download is restarted to continue from the last session.

The `raw` folder contains the raw data downloaded from the Somnofy server. The data is stored in the `json` format. Each session is stored in a separate file. The file name is the DATE-SESSION_ID.json. 
That way the raw data can be sorted by date.

The `data` folder contains the epoch data and sessions report in an *easy* to use form as data tables. The data is stored in the `csv` format. 
Whenever the download is started, the date range is established as START_DATE_OF_THE_FIRST_DOWNLOADED_SESSION to the END_DATE_OF_THE_LAST_FINISHED session.

For example if in the previous run the last downloaded session terminates on 2024-07-14 at 9:30, we run download in the afternoon of the 2024-07-26
the program will use as the date range: `2024-07-14_2024-07-26` 
(if there was a session on the 26th July).

The date-range is used to name the following files:

```
- 2024-07-14_2024-07-26_epoch_data.csv - with the epoch data withing the date range
- 2024-07-14_2024-07-26_session_report.csv - with the list of sessions and their characteristics in the date range
- 2024-07-14_2024-07-26_compliance_info.csv - with the information with the validy of each night in the date range 
```

additionally the  file `all_sessions_report.csv` contains characteristics of all the sessions which have been ever downloaded by the program, it can be used to find sessions for any day within the study.

### Epoch data

Simply saying epoch-dataf file contains the timeseries of the monitored variables for each session  withing the download date range  
(remember only the sessions of their duration larger than `ignore-epoch-for-shorter-than-hours` are included).

The epoch data contains the following columns:

| Column Name                  | Description                                                                                                                       |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `timestamp`                  | The timestamp of the 30 second epoch for which data row is created.                                                               |
| `session_id`                 | The Somnofy's unique identifier for the session.                                                                                  |
| `sleep_stage`                | The sleep stage as established with their algorithm.<br/> Their encoded as numbers 0-5 @TODO check the api docs about the meaning |
| `reliability`                | The reliability score of the data point.                                                                                          |
| `timestamp_utc`              | The UTC timestamp of the data point.                                                                                              |
| `num_of_data_in_epoch`       | The number of data points in the epoch (30).                                                                                      |
| `respiration_rate_mean`      | The mean respiration rate during the epoch.                                                                                       |
| `respiration_rate_var_mean`  | The mean variance of the respiration rate during the epoch.                                                                       |
| `movement_mean`              | The mean movement detected during the epoch.                                                                                      |
| `distance_mean`              | The mean distance to subject measured during the epoch.                                                                           |
| `signal_quality_mean`        | The mean signal quality during the epoch.                                                                                         |
| `heart_rate_mean`            | The mean heart rate during the epoch.                                                                                             |
| `heart_rate_var`             | The variance of the heart rate during the epoch.                                                                                  |
| `external_heart_rate_mean`   | The mean external heart rate during the epoch.                                                                                    |
| `external_heart_rate_var`    | The variance of the external heart rate during the epoch.                                                                         |
| `external_spo2_mean`         | The mean external SpO2 level during the epoch.                                                                                    |
| `external_spo2_var`          | The variance of the external SpO2 level during the epoch.                                                                         |
| `light_ambient`              | The ambient light level during the epoch.                                                                                         |
| `sound_amplitude`            | The sound amplitude during the epoch.                                                                                             |
| `temperature_ambient`        | The ambient temperature during the epoch.                                                                                         |
| `time_offset`                | The time offset in seconds from the start of the session.                                                                         |

### Compliance info

The compliance info file contains rows for each nights within the download date range with characteristics that help assess the validity of the sleep data, for example the number of sessions is 0 so the sensor must have been offline.

The compliance info contains the following columns:

| Column Name                | Description                                                                                                            |
|----------------------------|------------------------------------------------------------------------------------------------------------------------|
| `night_date`               | The date of the night for which sessions are being assessed. All sessions which session_end in this date are included. |
| `number_of_long_sessions`  | The number of sessions longer than the minimal duration specified in `ignore-epoch-for-shorter-than-hours`.            |
| `max_time_in_bed_h`        | The maximum time spent in bed during the night, in hours                                                               |
| `max_time_asleep_h`        | The maximum time spent asleep during the night, in hours.                                                              |
| `total_sleep_time_h`       | The total sleep time during the night, in hours. Calculated with time asleep for all not ignored session at this night |
| `valid`                    | True is the night is valide, which currently means: a) there are recordings for this date, b) the total sleep is >= `flag-short-sleep-for-less-than-hours`   |

### Session report

The session report file contains rows for ALL session within the download date range (they are not filtered with ignore). 
Apart from household information about the session (id, session_start, session_end), it contains the information about the sleep and activity.   



| Column Name                          | Description                                                  |
|--------------------------------------|--------------------------------------------------------------|
| `session_id`                         | The somnofy unique identifier for the session.               |
| `epoch_count`                        | The number of 30s epochs in the session.                     |
| `session_start`                      | The timestamp for start of the session.                      |
| `relative_session_start`             | @TODO check somnofy                                          |
| `session_end`                        | The timestamp for end of the session.                        |
| `time_at_last_epoch`                 | The timestamp  the last epoch of the session.                |
| `time_at_intended_sleep`             | The time of sleep attempt.                                   |
| `time_in_undefined`                  | The time spent in undefined (sleep) stage.                   |
| `time_at_sleep`                      | The fall asleep time.                                        |
| `time_at_wakeup`                     | The wakeup time.                                             |
| `sleep_onset`                        | The time it took to fall asleep in seconds.                  |
| `time_in_bed`                        | The total time spent in bed [s].                             |
| `time_asleep`                        | The total time scored as asleep in the session [s].          |
| `sleep_efficiency`                   | The efficiency of sleep.                                     |
| `time_in_light_sleep`                | The time spent in light sleep [s].                           |
| `time_in_rem_sleep`                  | The time spent in REM sleep [s].                             |
| `time_in_deep_sleep`                 | The time spent in deep sleep [s].                            |
| `time_in_no_presence`                | The time spent with no presence detected [s]                 |
| `number_of_times_no_presence`        | The number of times no presence was detected.                |
| `time_wake_after_sleep_onset`        | The time spent awake after sleep onset.                      |
| `number_of_times_awake`              | The number of times the subject woke up.                     |
| `number_of_times_awake_long`         | The number of times the subject woke up for a long duration. |
| `time_wake_pre_post_sleep`           | The time spent awake before and after sleep.                 |
| `sleep_onset_rem_period`             | The period of REM sleep onset.                               |
| `sleep_mean_movement`                | The mean movement during sleep.                              |
| `non_rem_mean_rpm`                   | The mean RPM (respirations per minute) during non-REM sleep. |
| `non_rem_mean_heartrate`             | The mean heart rate during non-REM sleep.                    |
| `non_rem_mean_external_heartrate`    | The mean external heart rate during non-REM sleep.           |
| `epochs_with_movement_pct`           | The percentage of epochs with movement.                      |
| `sleep_score_1`                      | The sleep score based on the first scoring method.           |
| `external_spo2_mean`                 | The mean external SpO2 level.                                |
| `air_pressure_mean`                  | The mean air pressure.                                       |
| `light_ambient_mean`                 | The mean ambient light level.                                |
| `sound_amplitude_mean`               | The mean sound amplitude.                                    |
| `temperature_mean`                   | The mean temperature.                                        |
| `indoor_air_quality_mean`            | The mean indoor air quality.                                 |
| `air_humidity_mean`                  | The mean air humidity.                                       |
| `ems_report_start`                   | The start time of the EMS report.                            |
| `time_offset_at_intended_sleep`      | The time offset at intended sleep.                           |
| `time_offset_at_intended_wakeup`     | The time offset at intended wakeup.                          |
| `time_offset_at_sleep`               | The time offset at sleep.                                    |
| `time_offset_at_wakeup`              | The time offset at wakeup.                                   |

### All sessions report

Is the same as session_report but contains all the sessions ever downloaded by the program. It can be used for example to find sessions for any day within the study.
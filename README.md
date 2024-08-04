# AmbientBD Somnofy data download

This a package for downloading sleep data from the radar devices and storing them in a "analysis friendly" formats.

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

## Data layout and format

For each subject a folder is created in the download folder. The folder name is the subject ID. Inside the subject folder, there are three subfolders: `data` and `row` and `sys`.

The `sys` folder contains the information used by the program to track the download status. For example it stores the last finished session which has been downloaded. This information is used when download is restarted to continue from the last session.

The `row` folder contains the raw data downloaded from the Somnofy server. The data is stored in the `json` format. Each session is stored in a separate file. The file name is the DATE-SESSION_ID.json. 
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

The epoch data contains the following columns:

### Data Dictionary

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
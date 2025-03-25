# 0.2.1 (in development)

**New features**
- Added a new command `ambient_check_devices` which checks the status of all devices in the current zone and shows their status in the logs
- Added an optional parameter to the config file: `device-check-dir` to set where the device check log is written (defaults to current directory)

# 0.2 (04/09/2023)

**New features**
- Target zone needs to be specified in the properties file

**Improvements**
- Reading the client ID will not fail if it is followed by a linebreak or space

# 0.3.0 (in dev)

- Changed Sessions and Epochs filenames to match the Ambient-BD naming convention

# 0.2.2 (17/06/2025)

**Fixes**
- Fixed date range displaying incorrectly in saved file names (e.g. reports and compliance files)
- Fixed error when device name could not be read from the data

# 0.2.1 (27/03/2025)

**Improvements**
- The "zone" field in the config file can now take several values, separated by commas. For example, `zone=ABD Pilot, ABD Work Package 1` will download data for both ABD Pilot and ABD Work Package 1 zones. Alternatively, using `*` will download data from all available zones (for example, `zone=*`)
- Added "subject" and "device" fields to the config file to download data only for specific subjects and/or devices. As for zones, multiple subjects can be separated by commas, or using a `*` will download all available data (for example, `subject=*`, `device=*`)

# 0.2 (28/02/2025)

**New features**
- Target zone needs to be specified in the properties file

**Improvements**
- Reading the client ID will not fail if it is followed by a linebreak or space

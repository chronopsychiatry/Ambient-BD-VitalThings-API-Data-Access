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

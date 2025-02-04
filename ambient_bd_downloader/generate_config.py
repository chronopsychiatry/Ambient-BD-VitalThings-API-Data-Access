def generate_config():
    with open('ambient_bd_downloader.properties', 'w') as f:
        f.write('[DEFAULT]\n')
        f.write('client-id-file=.\\client_id.txt\n')
        f.write('download-dir=.\\downloaded_data\n')
        f.write('from-date=2021-01-01\n')
        f.write('ignore-epoch-for-shorter-than-hours=2\n')
        f.write('flag-nights-with-sleep-under-hours=5')


generate_config()

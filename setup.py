from setuptools import setup, find_packages

setup(
    name='ambient_bd_downloader',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your project dependencies here.
        'pandas>=1.5.3',
        'requests>=2.31.0',
    ],
    entry_points={
        'console_scripts': [
            'ambient_download=ambient_bd_downloader:main.main',
            'ambient_generate_config=ambient_bd_downloader:generate_config.generate_config'
        ],
    },
)

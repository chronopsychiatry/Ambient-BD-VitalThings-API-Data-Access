from setuptools import setup, find_packages

setup(
    name='ambient_bd_downloader',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your project dependencies here.
        'requests>=2.31.0',
    ],
    entry_points={
        'console_scripts': [
            'ambient_download=main:main',  # 'your_command' is the command you'll use in the CLI.
        ],
    },
)


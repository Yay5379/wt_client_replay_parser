from setuptools import setup, find_packages

setup(
    name='wt_client_replay_parser',
    author='Yay5379',
    description='War Thunder client replay data extraction tool',
    url='https://github.com/Yay5379/wt_client_replay_parser',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={'': ['formats/blk.lark']},
)

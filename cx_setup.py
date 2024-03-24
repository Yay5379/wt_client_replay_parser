from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'console'

executables = [
    Executable('wrpl_unpacker.py', base=base),
    Executable('formats/parse_datablocks.py', base=base)
]

setup(name='wt_client_replay_parser',
      version = '1.0',
      author = 'Yay5379',
      url = 'https://github.com/Yay5379/wt_client_replay_parser',
      description = 'War Thunder client replay data extraction tool',
      options = {'build_exe': build_options},
      executables = executables)

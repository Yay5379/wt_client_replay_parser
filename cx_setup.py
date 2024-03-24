from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': ["unittest", "pydoc", "construct.examples", "bz2", "lib2to3", "test", "tkinter", "email"],
                 'includefiles': ["src/wt_client_replay_parser/formats/parse_datablocks.py", "src/wt_client_replay_parser/formats/parse_replay.py"]}

base = 'console'

executables = [
    Executable('src/wt_client_replay_parser/wrpl_unpacker.py', base=base),
    Executable('src/wt_client_replay_parser/formats/parse_datablocks.py', base=base)
]

setup(name='wt_client_replay_parser',
      version = '1.0',
      author = 'Yay5379',
      url = 'https://github.com/Yay5379/wt_client_replay_parser',
      description = 'War Thunder client replay data extraction tool',
      options = {'build_exe': build_options},
      executables = executables)

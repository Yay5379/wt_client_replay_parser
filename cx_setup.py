import os.path
import sys
from cx_Freeze import setup, Executable

src_path = "src/wt_client_replay_parser/"
packages = ["multiprocessing"]
includes = []
excludes = ["unittest", "pydoc", "construct.examples", "bz2", "lib2to3", "test", "tkinter", "email", "http", "xml", "xmlrpc"]
includefiles = []
zip_include_packages = ["collections", "construct", "ctypes", "encodings", "json", "logging", "importlib", "formats",
                        "distutils", "click", "pkg_resources", "chardet", "zlib", "zstandard",
                        "multiprocessing", "multiprocessing-logging", "blk"]

wrpl_unpacker = Executable(
    script=os.path.join(src_path, "wrpl_unpacker.py")
)

parse_datablocks = Executable(
    script=os.path.join(src_path, "formats/parse_datablocks.py")
)

setup(
    name="wt_client_replay_parser",
    author='Yay5379',
    description="War Thunder client replay data extraction tool",
    url="https://github.com/Yay5379/wt_client_replay_parser",
    options={"build_exe": {"includes": includes, "excludes": excludes, "include_files": includefiles,
                           "packages": packages, "zip_include_packages": zip_include_packages,
                           "path": sys.path + [src_path]}},
    executables=[wrpl_unpacker, parse_datablocks]
)

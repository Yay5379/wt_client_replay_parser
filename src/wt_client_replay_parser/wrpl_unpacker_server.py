import argparse
from pathlib import Path
import zlib
import typing as t
import os
import sys
import construct as ct
from blk.types import Section
import blk.text as txt
from formats.wrpl_parser import WRPLServFile
from formats.parse_datablocks import parse_datablocks


def serialize_text(root: Section, ostream: t.TextIO):
    txt.serialize(root, ostream, dialect=txt.StrictDialect)


def create_text(path: os.PathLike) -> t.TextIO:
    return open(path, 'w', newline='', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description='war thunder client replay parser')
    parser.add_argument('replay', type=argparse.FileType('rb'), help='path to WRPL file')
    parser.add_argument('-o', dest='out_dir', type=Path, default=Path.cwd(),
                        help='output directory %(default)s.')
    ns = parser.parse_args()
    replay = ns.replay
    replay_path = Path(replay.name)
    out_dir: Path = ns.out_dir / f'{replay_path.name}.d'

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print('error creating output directory {}: {}'.format(out_dir, e), file=sys.stderr)
        return 1
    
    try:
        parsed = WRPLServFile.parse_stream(replay)
    except:
        print('error parsing input file {}: {}'.format(replay.name, e), file=sys.stderr)
        return 1
    
    for name in ('m_set'):
        section = parsed[name]
        out_path = (out_dir / name).with_suffix('.blk')
        with create_text(out_path) as ostream:
            serialize_text(section, ostream)
    
    print(f'{replay.name} => {out_dir}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
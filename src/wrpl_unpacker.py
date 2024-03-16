"""
Распаковка клиентского реплея.

Вход:
#2021.09.20 19.30.33.wrpl

Выход:
#2021.09.20 19.30.33.wrpl.d/
├── m_set.blkx
├── rez.blkx
├── info.json
└── wrplu.bin
"""

import argparse
import json
from pathlib import Path
import typing as t
import os
import sys
import construct as ct
from blk.types import Section
import blk.text as txt
import blk.json as jsn
try:
    from formats.wrpl_parser import WRPLCliFile
except ImportError:
    from formats.wrpl_parser import WRPLCliFile
try:
    from formats.parse_datablocks import parse_datablocks
except ImportError:
    from formats.parse_datablocks import parse_datablocks
try:
    from formats.parse_replay import parse_replay
except ImportError:
    from formats.parse_replay import parse_replay

STRICT_BLK = 'strict_blk'
JSON = 'json'
JSON_2 = 'json_2'
JSON_3 = 'json_3'

out_type_map = {
    STRICT_BLK: txt.STRICT_BLK,
    JSON: jsn.JSON,
    JSON_2: jsn.JSON_2,
    JSON_3: jsn.JSON_3,
}


def suffix(out_format: str) -> str:
    return '.blkx' if out_format == STRICT_BLK else '.json'


def serialize_text(root: Section, ostream: t.TextIO, out_type: int, is_sorted: bool = False):
    if out_type == txt.STRICT_BLK:
        txt.serialize(root, ostream, dialect=txt.StrictDialect)
    elif out_type in (jsn.JSON, jsn.JSON_2, jsn.JSON_3):
        jsn.serialize(root, ostream, out_type, is_sorted)


def create_text(path: os.PathLike) -> t.TextIO:
    return open(path, 'w', newline='', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description='Распаковщик реплея.')
    parser.add_argument('replay', type=argparse.FileType('rb'), help='Файл реплея.')
    parser.add_argument('-o', dest='out_dir', type=Path, default=Path.cwd(),
                        help='Выходная директория. По умолчанию %(default)s.')
    parser.add_argument('--format', dest='out_format', choices=list(out_type_map), default=STRICT_BLK,
                        help='Формат для blk. По умолчанию %(default)s.')
    ns = parser.parse_args()
    replay = ns.replay
    out_format = ns.out_format
    out_type = out_type_map[out_format]
    replay_path = Path(replay.name)
    out_dir: Path = ns.out_dir / f'{replay_path.name}.d'

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print('Ошибка при создании выходной директории {}: {}'.format(out_dir, e), file=sys.stderr)
        return 1

    try:
        parsed = WRPLCliFile.parse_stream(replay)
    except ct.ConstructError as e:
        print('Ошибка при разборе входного файла {}: {}'.format(replay.name, e), file=sys.stderr)
        return 1

    for name in ('m_set', 'rez'):
        section = parsed[name]
        out_path = (out_dir / name).with_suffix(suffix(out_format))
        with create_text(out_path) as ostream:
            serialize_text(section, ostream, out_type)

    out_path = out_dir / 'wrplu.bin'
    out_path.write_bytes(parsed.wrplu)

    out_path = out_dir / 'info.json'
    info = {
        'difficulty': int(parsed.header.difficulty),
        'session_type': int(parsed.header.session_type),
        'battle_class': parsed.header.battle_class,
        'session_id': parsed.header.session_id,
        'start_time': parsed.header.start_time,
    }
    with create_text(out_path) as ostream:
        json.dump(info, ostream, indent=2)
    
    parse_datablocks(f'{out_dir}/wrplu.bin')
    data = parse_replay(f'{out_dir}/wrplu.bin')
    with create_text(f'{out_dir}/units.json') as ostream:
        json.dump(data, ostream, indent=2)

    print(f'{replay.name} => {out_dir}')

    return 0


if __name__ == '__main__':
    sys.exit(main())

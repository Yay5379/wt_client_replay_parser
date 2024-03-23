import argparse
import json
from pathlib import Path
import typing as t
import os
import sys
import construct as ct
from blk.types import Section
import blk.text as txt
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

def serialize_text(root: Section, ostream: t.TextIO):
    txt.serialize(root, ostream, dialect=txt.StrictDialect)


def create_text(path: os.PathLike) -> t.TextIO:
    return open(path, 'w', newline='', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description='Распаковщик реплея.')
    parser.add_argument('replay', type=argparse.FileType('rb'), help='Файл реплея.')
    parser.add_argument('-o', dest='out_dir', type=Path, default=Path.cwd(),
                        help='Выходная директория. По умолчанию %(default)s.')
    ns = parser.parse_args()
    replay = ns.replay
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
        out_path = (out_dir / name).with_suffix('.blk')
        with create_text(out_path) as ostream:
            serialize_text(section, ostream)

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

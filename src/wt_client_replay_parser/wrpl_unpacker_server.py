import argparse
from pathlib import Path
import typing as t
import os
import sys
import construct as ct
from blk.types import Section
import blk.text as txt
from formats.wrpl_parser import WRPLServFile


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
    except ct.ConstructError as e:
        print('error parsing input file {}: {}'.format(replay.name, e), file=sys.stderr)
        return 1
    
    for name in ('m_set',):
        section = parsed[name]
        out_path = (out_dir / name).with_suffix('.blk')
        with create_text(out_path) as ostream:
            serialize_text(section, ostream)

    # there is probably a better way to do this idk how and this works so... yeah...
    out_path = out_dir / 'info.blk'

    info=(
        f'wrplVersion:i={parsed.header.version}\n'
        f'level:t="{parsed.header.level}"\n'
        f'levelSettings:t="{parsed.header.level_settings}"\n'
        f'battleType:t="{parsed.header.battle_type}"\n'
        f'environment:t="{parsed.header.environment}"\n'
        f'visibility:t="{parsed.header.visibility}"\n'
        f'difficulty:i={parsed.header.difficulty}\n'
        f'srvId:i={parsed.header.srv_id}\n'
        f'sessionType:i={parsed.header.session_type}\n'
        f'sessionId:i={parsed.header.session_id}\n'
        f'replayNumber:i={parsed.header.server_replay_order_number}\n'
        f'weatherSeed:i={parsed.header.weather_seed}\n'
        f'locName:t="{parsed.header.loc_name}"\n'
        f'startTime:i={parsed.header.start_time}\n'
        f'timeLimit:i={parsed.header.time_limit}\n'
        f'scoreLimit:i={parsed.header.score_limit}\n'
        f'dynamicResult:i={parsed.header.dynamicResult}\n'
        f'gm:i={parsed.header.gm}\n'
        f'battleClass:t="{parsed.header.battle_class}"\n'
        f'battleKillStreak:t="{parsed.header.battle_kill_streak}"'
    )

    with create_text(out_path) as ostream:
        print(info, file=ostream)
    
    print(f'{replay.name} => {out_dir}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
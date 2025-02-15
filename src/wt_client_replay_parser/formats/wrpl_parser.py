import enum
import typing as t
import construct as ct
from construct import this
import blk.binary as bin


def no_encoder(obj, context):
    raise NotImplementedError()


def StringField(sz: t.Union[int, callable]) -> ct.Construct:
    return ct.FixedSized(sz, ct.CString('ascii'))


class Difficulty(enum.IntEnum):
    ARCADE = 0b0000
    REALISTIC = 0b0101
    HARDCORE = 0b1010


# todo: уточнить флаги
class SessionType(enum.IntEnum):
    AIR_SIM = 0x3C  # самолеты, симуляторные бои
    MARINE_BATTLE = 0x1a  # морские бои
    RANDOM_BATTLE = 0x20
    CUSTOM_BATTLE = 0x40  # полигон
    USER_MISSION = 0x01  # пользовательские миссии


class LocalPlayerCountry(enum.IntEnum):
    COUNTRY_USA = 0x01
    COUNTRY_GERMANY = 0x02
    COUNTRY_USSR = 0x03
    COUNTRY_BRITAIN = 0x04
    COUNTRY_JAPAN = 0x05
    COUNTRY_CHINA = 0x06
    COUNTRY_ITALY = 0x07
    COUNTRY_FRANCE = 0x08
    COUNTRY_SWEEDEN = 0x09
    COUNTRY_ISRAEL = 0x0A


DifficultyCon = ct.ExprAdapter(ct.Bitwise(ct.FocusedSeq(
    'difficulty',
    'unk_nib' / ct.BitsInteger(4),
    'difficulty' / ct.BitsInteger(4))),
    lambda obj, context: Difficulty(obj),
    no_encoder
)


Header = ct.Struct(
    'magic' / ct.Const(bytes.fromhex('e5ac0010')),
    'version' / ct.Int32ul,  # 2.9.0.38 ~ 101111
    'level' / StringField(128),  # levels/avg_stalingrad_factory.bin
    'level_settings' / StringField(260),  # gamedata/missions/cta/tanks/stalingrad_factory/stalingrad_factory_dom.blk
    'battle_type' / StringField(128),  # stalingrad_factory_Dom
    'environment' / StringField(128),  # day
    'visibility' / StringField(32),  # good
    'rez_offset' / ct.Int32ul,  # not used for server replays
    'difficulty' / DifficultyCon,
    'unk_3' / ct.Bytes(3),
    'srv_id' / ct.Int8ul,
    'unk_31' / ct.Bytes(31),
    'session_type' / ct.Int32ul,  # меня интересует только RANDOM_BATTLE для танков
    'session_id' / ct.Int64ul,
    'server_replay_order_number' / ct.Int16ul,  # the number from the title of the server replay ex: 0001.wrpl. always 0 for client replays
    'unk_int16' / ct.Int16ul,
    'weather_seed' / ct.Int32ul,
    'm_set_size' / ct.Int64ul,
    'unk_19' / ct.Bytes(19),
    'local_player_country' / ct.Int8ul,
    'unk_4' / ct.Bytes(4),
    'loc_name' / StringField(128),  # missions/_Dom;stalingrad_factory/name
    'start_time' / ct.Int32ul,
    'time_limit' / ct.Int32ul,
    'score_limit' / ct.Int64ul,
    'unk_8' / ct.Bytes(8),
    'local_player_id' / ct.Int8ul,  # always 0 for server replays
    'unk_2' / ct.Bytes(2),
    'unk_Int8ul' / ct.Int8ul,
    'unk_28' / ct.Bytes(28),
    'gm' / ct.Int32ul,
    'battle_class' / StringField(128),  # air_ground_Dom
    'battle_kill_streak' / StringField(128),  # killStreaksAircraftOrHelicopter_1
)


def FatBlockStream(sz: t.Union[int, callable, None] = None) -> ct.Construct:
    con = ct.GreedyBytes if sz is None else ct.Bytes(sz)
    return ct.RestreamData(con, bin.Fat)


WRPLCliFile = ct.Struct(
    'header' / Header,
    ct.Bytes(2),
    'm_set' / FatBlockStream(this.header.m_set_size),
    'wrplu_offset' / ct.Tell,
    'wrplu' / ct.Bytes(this.header.rez_offset - this.wrplu_offset),
    'rez' / bin.Fat,
)


WRPLServFile = ct.Struct(
    'header' / Header,
    ct.bytes(2),
    'm_set' / FatBlockStream(this.header.m_set_size),
    'rest_of_file' / ct.Tell,
    'headless_file' / ct.Bytes(this.rest_of_file),
)
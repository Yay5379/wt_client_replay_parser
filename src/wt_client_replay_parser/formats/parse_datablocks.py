import os
import re
import sys
import blk.binary as bin
import blk.text as txt
import typing as t
from io import BytesIO
from blk.types import Section

# creats a datablock (.blk) file
def create_text(name:str, id:int, path) -> t.TextIO:
    file_path = os.path.dirname(path)
    if not os.path.exists(f'{file_path}/units'):
        os.mkdir(f'{file_path}/units')
    if os.path.exists(f'{file_path}/units/{name}({id}).blk'):
        pass
    else:
        return open(f'{file_path}/units/{name}({id}).blk', 'x')
    
# appends more data to a datablock (.blk) file    
def append_block(name:str, id:int, path) -> t.TextIO:
    file_path = os.path.dirname(path)
    return open(f'{file_path}/units/{name}({id}).blk', 'a')
    
# writes data to a file
def serialize_text(root:Section, ostream:t.TextIO, data:str):
    if root is None:
        print(data, file=ostream)
    elif data == 'append':
        print(f'\n', file=ostream)
        txt.serialize(root, ostream, dialect=txt.StrictDialect)
    else:
        print(data, file=ostream)
        txt.serialize(root, ostream, dialect=txt.StrictDialect)

def _get_text(bstring, letters=None):
    """
    from a binary string, return a text string where only the allowed letters are in
    """

    if letters is None:
        letters = list(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_")

    text = ""
    idx = 0
    while (letter := bstring[idx]) in letters and idx < len(bstring):
        text += chr(letter)
        idx += 1

    return text

# parses unit blk data
def parse_datablocks(path:str):

    magic = re.compile(b'\x01\x20\x01')

    ignored_vehicles = ["dummy_plane"]

    with open(path, 'rb') as f:
        replay = f.read()
    
    for m in magic.finditer(replay):
        try:
            vehicle = _get_text(replay[m.end() + 1:m.end() + 255])

            if len(vehicle) > 2 and vehicle not in ignored_vehicles:

                unit_id = replay[m.start() - 4]
                
                vehicle_len = replay[m.end()]

                weapon_preset_len = replay[m.end() + vehicle_len + 1]

                weapon_preset = _get_text(replay[m.end() + len(vehicle) + 2:m.end() + 255]) if weapon_preset_len > 0 else "default"

                skin_len = replay[m.end() + vehicle_len + weapon_preset_len + 2]

                skin = _get_text(replay[m.end() + len(vehicle) + len(weapon_preset) + 3:m.end() + 255]) if skin_len > 0 else "default"

                datablock_magic = replay[m.end() + vehicle_len + weapon_preset_len + skin_len + 5]

                if len(skin) != skin_len and skin != "default":
                    skin = skin.rstrip(skin[-1])

                if datablock_magic == 1:
                    print(f"parsing {vehicle}({unit_id})")
                        
                    unit_data=(
                    f'unitId:i={unit_id}\n'
                    f'vehicle:t="{vehicle}"\n'
                    f'weapon:t="{weapon_preset}"\n'
                    f'skin:t="{skin}"'
                    )

                    datablock_reader = BytesIO(replay[m.end() + vehicle_len + weapon_preset_len + skin_len + 5:m.end() + 4096])

                    datablock_stream = datablock_reader.read()

                    datablock1 = BytesIO(replay[m.end() + vehicle_len + weapon_preset_len + skin_len + 5:m.end() + 2048])

                    with datablock1 as istream:
                        try:
                            root = bin.compose_fat(istream)
                            with create_text(vehicle, unit_id, path) as ostream:
                                serialize_text(root, ostream, unit_data)
                        except:
                            pass
                    
                    datablock2_pattern = re.compile(b'\x61\x74\x74\x61\x63\x68\x61\x62\x6c\x65') #'attachable'

                    for m in datablock2_pattern.finditer(datablock_stream):

                        has_preset = datablock_stream[m.start() - 13]

                        if has_preset == 7:
                            datablock2 = BytesIO(datablock_stream[m.start() - 14:m.start() + 2048])

                            with datablock2 as istream:
                                try:
                                    root = bin.compose_fat(istream)
                                    with append_block(vehicle, unit_id, path) as ostream:
                                        serialize_text(root, ostream, 'append')
                                except:
                                    pass
                        else:
                            datablock2 = BytesIO(datablock_stream[m.start() - 3:m.start() + 2048])

                            with datablock2 as istream:
                                try:
                                    root = bin.compose_fat(istream)
                                    with append_block(vehicle, unit_id, path) as ostream:
                                        serialize_text(root, ostream, 'append')
                                except:
                                    pass

                else:
                    print(f"parsing {vehicle}({unit_id})")

                    unit_data=(
                    f'unitId:i={unit_id}\n'
                    f'vehicle:t="{vehicle}"\n'
                    f'weapon:t="{weapon_preset}"\n'
                    f'skin:t="{skin}"'
                    )

                    with create_text(vehicle, unit_id, path) as ostream:
                        serialize_text(None, ostream, unit_data)
        except:
            pass

def main():
    file = os.path.abspath(sys.argv[1])

    print(f"parsing replay in {file}")

    parse_datablocks(file)

if __name__ == "__main__":
    main()
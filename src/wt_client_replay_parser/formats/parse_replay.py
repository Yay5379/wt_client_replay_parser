import os
import re
import sys
import json

def parse_replay(file):

    units = []
    print(f"parsing {file}")
    units += _parse_replay_file(file)
    
    # join the unit ids
    units2 = []

    for uid in set([u["unit_id"] for u in units]):
        vehicles = []
        for v in list(set([u["vehicle"] for u in units if u["unit_id"] == uid])):
            for w in list(set([u["weapon_preset"] for u in units if u["unit_id"] == uid and u["vehicle"] == v])):
                for s in list(set([u["skin"] for u in units if u["unit_id"] == uid and u["vehicle"] == v])):
                    vehicles.append(
                    {
                        "vehicle": v,
                        "weaponPreset": w,
                        "skin" : s,
                        "numAppearances": len([u for u in units if u["unit_id"] == uid and u["vehicle"] == v])
                    }
            )
        units2.append({
            "unitId" : uid,
            "vehicles": vehicles,
            "numAppearances": len([u for u in units if u["unit_id"] == uid])
        })

    data = {}
    data['numUnits'] = len(units2)
    data['units'] = units2

    return data

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

def _parse_replay_file(path):
    """
    parse a single replay files and return instances of vehicles
    """

    # allowed letters for vehicle names
    # letters = list(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_")

    # magic which preceds vehicles
    magic = re.compile(b'\x01\x20\x01')

    # vehicles which are not player vehicles
    ignored_vehicles = ["dummy_plane"]

    with open(path, 'rb') as f:
        replay = f.read()
        
    units = []

    # find all magics in the replay file
    for m in magic.finditer(replay):
        
        # the byte before a name string determines its length so 255 is the max length 
        name_max_len = 255

        try:
            vehicle = _get_text(replay[m.start() + 4:m.start() + name_max_len])
        
            # only if the vehicle name is at least 2 letters, it is actually not garbage
            if len(vehicle) > 2 and vehicle not in ignored_vehicles:

                # player id can be found at the position m.start() - 4
                unit_id = replay[m.start() - 4]

                weapon_preset_len = replay[m.start() + len(vehicle) + 4]

                weapon_preset = _get_text(replay[m.start() + len(vehicle) + 5:m.start() + name_max_len]) if weapon_preset_len > 0 else "default"

                skin_len = replay[m.start() + len(vehicle) + len(weapon_preset) + 5]

                skin = _get_text(replay[m.start() + len(vehicle) + len(weapon_preset) + 6:m.start() + name_max_len]) if skin_len > 0 else "default"

                if len(skin) != skin_len and skin != "default":
                    skin = skin.rstrip(skin[-1])

                units.append({"unit_id" : unit_id, "vehicle" : vehicle, "weapon_preset" : weapon_preset, "skin" : skin})
        except:
            pass
    
    return units


def main():

    # if we have an argument, use this as path, otherwise use current folder
    file = os.path.abspath(sys.argv[1])

    print(f"parsing replay in {file}")

    data = parse_replay(file)

    folder_name = os.path.basename(file)
    file_path = os.getcwd()
    i = 2
    if os.path.exists(f'{file_path}/{folder_name}.json'):
        while os.path.exists(f'{file_path}/{folder_name}({i}).json'):
            i += 1
            with open(f'{file_path}/{folder_name}({i}).json', 'x') as ostream:
                json.dump(data, ostream, indent=2, separators=(',',':'))
    else:
        with open(f'{file_path}/{folder_name}.json', 'x') as ostream:
            json.dump(data, ostream, indent=2, separators=(',',':'))

    print()
    print(json.dumps(data, indent=2, separators=(',',':')))

if __name__ == "__main__":
    main()
import struct

path = "staging_gog_patch/Yakuza 0 Patch Vostfr by RGG Yakuza Rev 1.10/data/2dpar/ui_e.par"
with open(path, "rb") as f:
    magic, unkA, unkB, unkC, folder_cnt, folder_off, file_cnt, file_off = struct.unpack('>8I', f.read(32))
    name_start = 32 + 64 * folder_cnt
    f.seek(name_start)
    filenames = [f.read(64).split(b'\x00')[0].decode('latin1') for _ in range(file_cnt)]
    
    f.seek(file_off)
    file_entries = []
    for i in range(file_cnt):
        flags, uncomp_sz, comp_sz, offset, e, f_val, g, h = struct.unpack('>8I', f.read(32))
        file_entries.append((filenames[i], flags, uncomp_sz, comp_sz, offset))

keywords = ['ability', 'skill', 'congrat', 'dart', 'ufo', 'game_on', 'gameon', 'levelup', 'clear']
matched = []
for name, flags, uncomp_sz, comp_sz, offset in file_entries:
    if any(k in name.lower() for k in keywords):
        matched.append((name, offset, uncomp_sz))

print(f"Matched {len(matched)} outer files in ui_e.par:")
for m in matched:
    print(" ", m[0])

# Now check inside all inner PARs
all_inner_matches = []
for name, flags, uncomp_sz, comp_sz, offset in file_entries:
    if name.endswith('.par'):
        with open(path, "rb") as f:
            f.seek(offset)
            inner_data = f.read(min(uncomp_sz, 1024*1024))
        if inner_data[:4] == b'PARC':
            _, _, _, _, in_folders, in_foff, in_files, in_file_off = struct.unpack('>8I', inner_data[:32])
            in_name_start = 32 + 64 * in_folders
            in_names = [inner_data[in_name_start + i*64 : in_name_start + (i+1)*64].split(b'\x00')[0].decode('latin1') for i in range(in_files)]
            for in_n in in_names:
                if any(k in in_n.lower() for k in keywords):
                    all_inner_matches.append((name, in_n))

print(f"\nMatched {len(all_inner_matches)} inner files in ui_e.par:")
for parent, child in all_inner_matches[:20]:
    print(f"  {parent} -> {child}")

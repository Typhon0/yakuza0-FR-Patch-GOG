import struct, json

with open('scratch/Yakuza 0 Patch Vostfr by RGG Yakuza Rev 1.10/Yakuza0.exe', 'rb') as f:
    f.seek(0x1339200)
    trad_data = f.read(0x100000)

strings = []
curr = []
start = 0
for i, b in enumerate(trad_data):
    if b != 0:
        if not curr: start = i
        curr.append(b)
    else:
        if curr:
            strings.append((start, bytes(curr)))
            curr = []

french_strings = []
for off, s in strings:
    text = s.decode('latin1', errors='replace')
    # Filter for real French translations
    if 'CHAPITRE' in text or 'Commencer' in text or 'Quitter' in text or 'Chargez' in text or 'Deux joueurs' in text or 'Défiez' in text or 'Un mode' in text or 'Affichez' in text or 'Réglez divers' in text:
        french_strings.append((off, text))

print(f'Total identified French strings: {len(french_strings)}')
for off, t in french_strings:
    print(f'0x{off:X}: {repr(t)}')

with open('scratch/french_exe_strings.json', 'w', encoding='utf-8') as out:
    json.dump([t for _, t in french_strings], out, indent=2, ensure_ascii=False)

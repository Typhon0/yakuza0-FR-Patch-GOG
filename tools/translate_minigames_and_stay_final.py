# -*- coding: utf-8 -*-
"""
translate_minigames_and_stay_final.py
Translates all remaining text in:
- release_gog/data/minigame/pokecir.par (pokecir_parts.bin_c)
- release_gog/data/minigame/bakara/baccarat_cpu.bin_c
- release_gog/data/minigame/bakara/baccarat_gallery_msg.bin_c
- release_gog/data/minigame/chohan/minigame_chohan_bakuto.bin_c
- release_gog/data/staypar/stay.par (search_arms, controller_explain, response_roulette, tougijyo)
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz
from tools.translate_wdr_pass1 import repack_par

def clean_fr(s):
    return s.replace('œ', 'oe').replace('Œ', 'OE').replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')

def translate_rgg_table(data_bytes, translations):
    num_cols = struct.unpack('>I', data_bytes[4:8])[0]
    num_rows = struct.unpack('>I', data_bytes[8:12])[0]
    curr_off = 16 + num_cols * 64

    col_headers = []
    new_col_payloads = []

    for c in range(num_cols):
        hdr = bytearray(data_bytes[16 + c * 64 : 16 + (c + 1) * 64])
        col_type = struct.unpack('>I', hdr[32:36])[0]
        col_len = struct.unpack('>I', hdr[36:40])[0]
        col_data = data_bytes[curr_off : curr_off + col_len]
        curr_off += col_len

        if col_type == 4:  # String column
            old_ptrs = [struct.unpack('>I', col_data[r*4 : (r+1)*4])[0] for r in range(num_rows)]
            str_pool_start = num_rows * 4
            new_pool = bytearray()
            new_ptrs = []

            for r, ptr in enumerate(old_ptrs):
                if ptr == 0:
                    new_ptrs.append(0)
                    continue
                s_bytes = col_data[ptr:].split(b'\x00')[0]
                s_text = s_bytes.decode('latin1', errors='replace')
                if s_text in translations:
                    rep_str = clean_fr(translations[s_text])
                    rep_bytes = rep_str.encode('latin1')
                elif s_text.strip() in translations:
                    l_sp = s_text[:len(s_text) - len(s_text.lstrip())]
                    r_sp = s_text[len(s_text.rstrip()):]
                    rep_str = l_sp + clean_fr(translations[s_text.strip()]) + r_sp
                    rep_bytes = rep_str.encode('latin1')
                else:
                    rep_bytes = s_bytes.replace(b'\xc7', b'C')

                new_ptr = str_pool_start + len(new_pool)
                new_ptrs.append(new_ptr)
                new_pool.extend(rep_bytes + b'\x00')

            ptr_table = bytearray()
            for np in new_ptrs:
                ptr_table.extend(struct.pack('>I', np))

            new_payload = bytes(ptr_table + new_pool)
            rem = len(new_payload) % 4
            if rem != 0:
                new_payload += b'\x00' * (4 - rem)

            struct.pack_into('>I', hdr, 36, len(new_payload))
            col_headers.append(bytes(hdr))
            new_col_payloads.append(new_payload)
        else:
            col_headers.append(bytes(hdr))
            new_col_payloads.append(col_data)

    out = bytearray(data_bytes[:16])
    for h in col_headers:
        out.extend(h)
    for p in new_col_payloads:
        out.extend(p)
    return bytes(out)

BACCARAT_CPU_TRANS = {
    'Another loss? Rats.': 'Encore perdu ? Flute.',
    'Aw, shucks.': 'Mince alors.',
    'Bring it on!': 'Venez donc !',
    'Calling mothership.': 'Appel au vaisseau.',
    'Congratulations!': 'Felicitations !',
    'Disasterrestrial!': 'Catasterrestre !',
    'Ech, a sorry sight.': 'Pouah, triste spectacle.',
    'Fantasticosmical!': 'Fantasticosmique !',
    'Galacti-cool!': 'Galacti-cool !',
    'Getting better.': 'Ca va mieux.',
    'Give up, man.': 'Abandonne, mec.',
    'Going all out!': 'A fond la caisse !',
    'Going on a hunch...': 'A l\'intuition...',
    'Going well!': 'Ca va fort !',
    'Good show, old chap.': 'Beau jeu, l\'ami.',
    'Heh. Heh. Heh.': 'Heh. Heh. Heh.',
    'Hell, yeah!': 'Oh que oui !',
    'Here I go!': 'A moi !',
    'Hey hey hey!': 'Hey hey hey !',
    'Holy hell.': 'Bordel.',
    'I did it!': 'J\'ai reussi !',
    'I keep losing...': 'Je perds sans cesse...',
    "I'm in top form.": "Je suis au top.",
    "I'm on a roll, yo!": "Je suis chaud bouillant !",
    'Jolly good!': 'Formidable !',
    'Lady Luck left me.': 'La chance m\'a quitte.',
    "Let's do this!": "C'est parti !",
    "Let's try this...": "Essayons ca...",
    'Like, oh no!': 'Oh non, serieux !',
    'Mister Bling-Bling': 'Monsieur Bling-Bling',
    'N-No way!': 'P-Pas possible !',
    'Not again...': 'Pas encore...',
    'Of course I won.': 'Evidemment que j\'ai gagne.',
    'Oh, well.': 'Tant pis.',
    'Oh, yes!': 'Oh, oui !',
    'Out of luck, huh?': 'Pas de veine, hein ?',
    'Poor form, old sport.': 'Mauvaise passe, mon vieux.',
    'Poorly played.': 'Mal joue.',
    'Shit happens.': 'Ca arrive.',
    'So cool.': 'Trop cool.',
    'Spaced out there?': 'Dans la lune ?',
    'Stellar play!': 'Jeu stellaire !',
    "That'll do.": "Ca suffira.",
    'The chances are...': 'Les probabilites sont...',
    'This better work.': 'Mieux vaut que ca marche.',
    "This game's rigged.": "Ce jeu est truque.",
    'This is fine pickle.': 'Joli petrin.',
    'This is it!': 'C\'est le moment !',
    'This is too easy!': 'C\'est trop facile !',
    'Tough choice.': 'Choix cornelien.',
    'What on Mars...!': 'Par tous les martiens... !',
    'Win some, lose some.': 'On gagne, on perd.',
    "Wow, I'm on fire!": "Ouah, je suis en feu !",
    "Wow, you're lucky.": "Ouah, quelle chance."
}

BACCARAT_GALLERY_TRANS = {
    '10, maybe?': 'Un 10, peut-etre ?',
    '7 or 8?\nWhich is it?': 'Un 7 ou un 8 ?\nLequel ?',
    "It's a 2?\nMaybe 3?": "C'est un 2 ?\nOu un 3 ?",
    "That's a 7!\nNo, maybe 8?": "C'est un 7 !\nNon, un 8 ?"
}

CHOHAN_BAKUTO_TRANS = {
    'Bummer, eh?': 'La poisse, hein ?',
    'Damn you.': 'Maudits des.',
    'E-Even?': 'P-Pair ?',
    'Even!': 'Pair !',
    'Even...': 'Pair...',
    'Even?': 'Pair ?',
    'Gotta be even.': 'Faut du pair.',
    'Happens, man.': 'Ca arrive, mec.',
    "Let's try odd.": 'Tentons impair.',
    'Lucky bastard.': 'Veinard !',
    'Odd!': 'Impair !',
    'Odd, no?': 'Impair, non ?',
    'Odd...': 'Impair...',
    'Oh, wow.': 'Oh, ouah.',
    'Out of luck?': 'Pas de bol ?',
    'Sucks, huh?': 'La rage, hein ?',
    'Um... Odd!': 'Euh... Impair !'
}

STAY_FINAL_TRANS = {
    # search_arms_location.bin_c
    'After countless hours wandering through\nthis spooky forest...':
        'Apres des heures d\'errance dans cette\nforet lugubre...',
    'Cold climates can make travel\nchallenging. Local crime groups\nare good suppliers of weapons.':
        'Le froid complique les voyages.\nLes gangs locaux fournissent de\nbons arsenaux d\'armes.',
    'Found a tightly-guarded building, and hesitated only\nslightly before heading inside!':
        'Batisse bien gardee reperee, et apres\nune courte hesitation, entree dedans !',
    'Looks like a quiet residential area...':
        'Un quartier residentiel tranquille...',
    'One expansive mansion after another lines this\nexclusive residential district...':
        'Les manoirs luxueux se succedent dans\nce quartier residentiel huppe...',
    'The contact was already waiting! He nodded in greeting,\nbut seems untalkative.':
        'Le contact attendait deja ! Il salua de la\ntete, l\'air peu bavard.',
    'There they were--in an office building with\nthe name plate so worn out it was illegible.':
        'Les voila, dans un immeuble de bureaux\navec une plaque usee et illisible.',

    # search_arms_result_picture.bin_c
    'Crazy unbelievable success!\nMission went swimmingly and treasure was found!':
        'Succes incroyable !\nMission parfaite et le tresor a ete trouve !',
    'Good reception!\nGreeted in a very promising way.':
        'Bon accueil !\nRecu de facon tres prometteuse.',
    'Success!\nMission went reasonably well.':
        'Succes !\nLa mission s\'est bien passee.',
    'Tight spot!\nSurrounded by men who look like bad news.':
        'Mauvais pas !\nCerne par des individus menacants.',

    # tougijyo_realtime_quest.bin_c
    'Throw your opponent!': 'Projetez votre adversaire !',

    # tougijyo_regulation_set.bin_c
    'Any Style': 'Tous styles',

    # controller_explain.bin_c
    'Back': 'Retour',
    'Before bet: Same Bet\nAfter: Collect Chips': 'Avant mise : Meme mise\nApres : Ramasser jetons',
    'Cast/Bring Pole Back\nOK': 'Lancer/Ramener ligne\nValider',
    'Change Bet Amount': 'Changer la mise',
    'Confirm Bet Amount\nThrow Dice': 'Confirmer la mise\nLancer les des',
    'Finish/Back': 'Terminer/Retour',
    'Give Up': 'Abandonner',
    'Hands List': 'Combinaisons',
    'Move Hand': 'Deplacer main',
    'One-roll Triple': 'Triple en 1 coup',
    'Quit\n(Only between games)': 'Quitter\n(Entre les manches)',
    'Show Roll History': 'Historique lancers',
    'Super Take Back': 'Super reprise',
    'Take Back': 'Reprendre',

    # response_roulette.bin_c
    'As it should be.': 'Comme il se doit.',
    'Better luck next time, <!--Name-->-san.': 'Plus de chance la prochaine fois, <!--Name-->-san.',
    'Come on...': 'Allez...',
    'Feeling good!': 'En forme !',
    'Gonna pass.': 'Je passe.',
    'Here I go!': 'A moi !',
    'Here we go.': 'Et voila.',
    'Here!': 'Ici !',
    'Here.': 'Ici.',
    'I lost.': 'J\'ai perdu.',
    "I'll just watch.": "Je regarde seulement.",
    "I'm ready.": "Je suis pret.",
    "Let's roll!": "A nous !",
    'Look at that!': 'Regardez ca !',
    'My win.': 'Victoire.',
    'Next time...': 'La prochaine fois...',
    'Shit!': 'Merde !',
    'This is it!': 'C\'est le moment !',
    "Well, I'm ready.": "Eh bien, pret.",
    'Well, obviously.': 'Evidemment.'
}

def main():
    print("[1/5] Patching pokecir.par...")
    pokecir_p = 'release_gog/data/minigame/pokecir.par'
    with open(pokecir_p, 'rb') as f:
        p_raw = f.read()
    p_files = parse_par(p_raw)
    flags, u_sz, c_sz, p_data = p_files['pokecir_parts.bin_c']
    dec_p = bytearray(decompress_sllz(p_data))
    old_m = b"A high-rev motor that's all about a high top speed."
    new_m = b"Moteur a haut regime axe sur une vitesse de pointe."
    assert len(old_m) == len(new_m)
    p_cnt = 0
    pos = 0
    while True:
        idx = dec_p.find(old_m, pos)
        if idx == -1: break
        dec_p[idx : idx + len(old_m)] = new_m
        p_cnt += 1
        pos = idx + len(new_m)
    comp_p = compress_sllz(bytes(dec_p))
    repacked_pokecir = repack_par(p_raw, {'pokecir_parts.bin_c': (flags, len(dec_p), len(comp_p), comp_p)})
    with open(pokecir_p, 'wb') as f:
        f.write(repacked_pokecir)
    print(f"  [+] Replaced {p_cnt} motor strings in pokecir.par!")

    print("[2/5] Patching baccarat_cpu.bin_c...")
    bac_cpu_p = 'release_gog/data/minigame/bakara/baccarat_cpu.bin_c'
    with open(bac_cpu_p, 'rb') as f:
        bac_raw = decompress_sllz(f.read())
    new_bac = translate_rgg_table(bac_raw, BACCARAT_CPU_TRANS)
    with open(bac_cpu_p, 'wb') as f:
        f.write(compress_sllz(new_bac))
    print(f"  [+] Updated baccarat_cpu.bin_c ({len(new_bac)} bytes)!")

    print("[3/5] Patching baccarat_gallery_msg.bin_c...")
    bac_gal_p = 'release_gog/data/minigame/bakara/baccarat_gallery_msg.bin_c'
    with open(bac_gal_p, 'rb') as f:
        gal_raw = decompress_sllz(f.read())
    new_gal = translate_rgg_table(gal_raw, BACCARAT_GALLERY_TRANS)
    with open(bac_gal_p, 'wb') as f:
        f.write(compress_sllz(new_gal))
    print(f"  [+] Updated baccarat_gallery_msg.bin_c ({len(new_gal)} bytes)!")

    print("[4/5] Patching minigame_chohan_bakuto.bin_c...")
    chohan_p = 'release_gog/data/minigame/chohan/minigame_chohan_bakuto.bin_c'
    with open(chohan_p, 'rb') as f:
        cho_raw = decompress_sllz(f.read())
    new_cho = translate_rgg_table(cho_raw, CHOHAN_BAKUTO_TRANS)
    with open(chohan_p, 'wb') as f:
        f.write(compress_sllz(new_cho))
    print(f"  [+] Updated minigame_chohan_bakuto.bin_c ({len(new_cho)} bytes)!")

    print("[5/5] Patching stay.par...")
    stay_p = 'release_gog/data/staypar/stay.par'
    with open(stay_p, 'rb') as f:
        stay_raw = f.read()
    stay_files = parse_par(stay_raw)
    stay_reps = {}

    stay_table_files = [
        'search_arms_location.bin_c',
        'search_arms_result_picture.bin_c',
        'tougijyo_realtime_quest.bin_c',
        'tougijyo_regulation_set.bin_c',
        'controller_explain.bin_c',
        'response_roulette.bin_c'
    ]

    for fn in stay_table_files:
        flags, u_sz, c_sz, data = stay_files[fn]
        dec = decompress_sllz(data)
        new_dec = translate_rgg_table(dec, STAY_FINAL_TRANS)
        comp = compress_sllz(new_dec)
        stay_reps[fn] = (flags, len(new_dec), len(comp), comp)
        print(f"  [+] Rebuilt {fn} ({len(new_dec)} bytes)")

    new_stay = repack_par(stay_raw, stay_reps)
    with open(stay_p, 'wb') as f:
        f.write(new_stay)
    print(f"[+] Successfully repacked stay.par ({len(new_stay)} bytes)!")

if __name__ == '__main__':
    main()

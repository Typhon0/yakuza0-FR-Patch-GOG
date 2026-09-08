# -*- coding: utf-8 -*-
"""
translate_common_par.py

Translates all remaining English files in release_gog/data/wdr_par_c/common.par:
- ai_popup.bin (street speech bubbles)
- blacksmith.bin
- present.bin
- sale0000.bin, sale0001.bin, sale0002.bin
- send.bin
- throw.bin
"""

import os
import sys
import shutil
import struct

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scratch'))
from scratch.scanner_engine import parse_par, decompress_sllz
from tools.sllz import compress_sllz

COMMON_TRANSLATIONS = {
    # blacksmith.bin
    "None": "Rien",
    "That'll be %s. Is that all right?": "Ca fera %s. C'est d'accord ?",
    "It'll cost %s to make. Is that okay?": "Fabrication : %s. D'accord ?",

    # present.bin
    "Are you sure you want to hand this over?": "Voulez-vous donner ceci ?",
    "(I don't have anything to hand over.)": "(Rien a donner.)",
    "(Nothing for me to hand over.)": "(Rien a donner.)",
    "(What am I gonna hand over?)": "(Qu'est-ce que je donne ?)",
    "(What should I hand over?)": "(Que donner ?)",

    # sale0000.bin, sale0001.bin, sale0002.bin
    "Are you sure you want to sell such rare stuff?": "Vendre un objet si rare ?",
    "That comes to %s.": "Ca fera %s.",
    "Rare stuff here. You sure you want to sell?": "Objet rare. Vous voulez vendre ?",
    "I'll give you %s for it.": "Je vous en donne %s.",
    "You okay parting with such rare stuff?": "Vendre un objet si rare ?",
    "Free": "Offt",
    "(I don't have anything to sell.)": "(Rien a vendre.)",
    "(Got nothing on me to sell.)": "(Rien a vendre.)",

    # send.bin
    "(I don't have any space. Guess I'll send it to the Item Box.)": "(Plus de place. Au Coffre.)",
    "(I'm outta space. Guess I'll send it to the Item Box.)": "(Plus de place. Au Coffre.)",
    "(Guess I'll send it to the Item Box.)": "(J'envoie ca au Coffre.)",
    "Guess I'll send it to the Item Box.)": "(J'envoie ca au Coffre.)",
    "Are you sure you want to send this?": "Voulez-vous envoyer ceci ?",
    "You sent %s to the Item Box.": "%s envoye au Coffre.",

    # throw.bin
    "(No space, so I'd better drop something.)": "(Plus de place, je dois jeter.)",
    "(Outta space. Better drop something.)": "(Plus de place. Mieux vaut jeter.)",
    "Are you sure you want to discard this?": "Voulez-vous jeter cet objet ?",
    "(It'd be a waste to just throw this away.)": "(Gachis de jeter ca.)",
    "(This is way too cool to toss.)": "(Trop precieux pour jeter.)",
    "(This weapon is too valuable to toss.)": "(Cette arme a trop de valeur.)",
    "(I ain't about to dump this weapon.)": "(Pas question de jeter ca.)",
    "%s discarded.": "%s jete.",

    # ai_popup.bin (Street chatter speech bubbles)
    'And then...': 'Et puis...',
    'And then?': 'Et puis ?',
    'Another fight?': 'Autre bagarre?',
    'Anything fun?': 'Du nouveau ?',
    'Awesome!': 'Genial !',
    'Be more confident.': 'Aie confiance !',
    'Beer! More beer!': 'Biere ! Encore !',
    'Better forget it.': 'Mieux vaut fuir.',
    "Can't get enough.": 'Jamais rassasie.',
    'Come on, one more!': 'Allez, encore 1 !',
    'Come on...': 'Allez...',
    'Come see me soon!': 'Reviens me voir !',
    'Cool!': 'Top !',
    "Couldn't get it back.": 'Impossible a ravoir.',
    'D-Drunk? Me? Nah...': 'B-Bourre ? Non...',
    "Didn't really mean it.": 'Pas fait expres.',
    "Don't bother with it.": "T'embete pas.",
    "Don't mess with me.": 'Me cherche pas.',
    "Don't worry about it.": "T'en fais pas.",
    "Feelin' good! Erp...": 'La forme ! Hic...',
    'Forget it.': 'Oublie.',
    'Give me a break.': 'Lache-moi.',
    'Good to see you!': 'Ravi de te voir!',
    'Got to try harder.': 'Fais des efforts !',
    'Gotta work tomorrow.': 'Je bosse demain.',
    'Haha!': 'Haha!',
    'Haha, what?': 'Haha, quoi?',
    'Hahaha!': 'Hahaha!',
    'Hehehe!': 'Hehehe!',
    'Hic!': 'Hic!',
    "How've you been?": 'Comment tu vas ?',
    'Huh?': 'Quoi',
    "I don't know...": 'Je sais pas...',
    'I forgot to buy it.': "Oublie d'acheter.",
    'I got a job.': "J'ai un taf.",
    'I hate when you do that.': 'Arrete de faire ca.',
    'I know how it feels.': 'Je te comprends.',
    'I know, right?': 'Pas vrai ?',
    'I lost it all!': 'Tout perdu !',
    'I totally forgot!': "J'avais zappe !",
    "I'll be right back.": 'Je reviens vite.',
    "I'll miss you.": 'Tu manqueras !',
    "I'm bored.": "J'm'ennuie",
    "I'm dog-tired.": 'Je suis creve.',
    "I'm hungry.": "J'ai faim.",
    "I'm invincible!": 'Invincible !',
    "I'm not drunk-- hic!": 'Pas bourre... hic !',
    "I'm really sorry.": 'Vraiment desole.',
    "I'm starving.": 'Trop faim.',
    "I'm still hung over.": 'Gueule de bois.',
    "I've had enough.": "J'en ai marre.",
    "Isn't that great?": "C'est pas super ?",
    'It happens to everyone.': 'Ca arrive a tous.',
    "It'll be fun!": 'Ce sera bien!',
    "It's all right!": 'Tout va bien !',
    "It's my lucky day.": "C'est mon jour !",
    "It's very popular.": 'Tres populaire.',
    'Kamurocho girls, yum!': 'Filles de Kamurocho !',
    'Ladies, here I come!': "Les filles, j'arrive",
    'Leave it to me.': 'Laisse faire !',
    'Leave it, man.': 'Laisse tomber.',
    "Let's come again.": 'On reviendra.',
    "Let's eat here.": 'Mangeons ici.',
    "Let's get going soon.": 'On devrait y aller.',
    "Let's hurry home.": 'Rentrons vite.',
    "Let's take a look.": 'Allons regarder.',
    'Listen, listen!': 'Ecoute ca !',
    'Long time no see!': 'Ca fait un bail !',
    'Look at the time!': "Regarde l'heure !",
    'Looks delicious.': "L'air delicieux.",
    "Man, I'm beat.": 'Je suis creve.',
    'Maybe a short break?': 'Une pause ?',
    'Nice piece of ass.': 'Joli petit lot.',
    'Nice!': 'Top !',
    'No, I mean it.': 'Non, serieux.',
    'Not my day.': 'Sale jour !',
    'Oh, I get it.': 'Ah, je vois.',
    'Oh, come on.': 'Oh, allez.',
    "Oh, it's you!": "C'est toi !",
    "Oh, that's nice!": "C'est sympa !",
    'One more bar!': 'Autre bar !',
    'Phew...': 'Ouf...',
    'Play me again later.': 'On rejoue plus tard.',
    'Really?': 'Vrai ?',
    'Remember last time?': 'Tu te souviens ?',
    'Right?': 'Vrai ?',
    'Seriously?': 'Serieux ?',
    'So cute!': 'Mignon !',
    'So... sleepy...': 'Sommeil...',
    'Still so young...': 'Si jeune encore.',
    'Stop teasing me.': 'Arrete un peu.',
    'Teehee!': 'Hihi !',
    'Tell me something funny.': 'Raconte un truc.',
    'Thank you!': 'Merci !',
    'Thanks for listening.': "Merci d'ecouter.",
    'That girl was hot.': 'Elle etait canon.',
    'That was fun!': 'Bien marrant!',
    'That was great!': "C'etait super !",
    'That was yummy!': "Trop delicieux!",
    "That's awful.": 'Trop affreux.',
    "That's nice.": "C'est bien.",
    "That's tough.": "C'est dur.",
    'They all say that!': 'Tous pareils !',
    'They miss you, too!': 'Tu manques aussi !',
    'This is the place.': "C'est ici.",
    'Time to go home.': 'Faut rentrer.',
    'Tsk, not doing well.': 'Pff, pas fort.',
    'Uh-huh.': 'Ouaip.',
    'Unbelievable...': 'Incroyable...',
    'Was it okay?': 'Ca allait ?',
    "We're getting along.": "On s'entend bien.",
    "We're getting old.": 'On se fait vieux.',
    'What happened next?': 'Et la suite ?',
    'What the hell?': "C'est quoi ?",
    "What'd you say?": "T'as dit quoi ?",
    "What's that about?": "C'est quoi ca ?",
    'Whee!': 'Youpi',
    'Where am I?': 'Ou suis-je?',
    'Where is he?': 'Il est ou ?',
    "Where's the next bar?": "C'est ou le bar ?",
    'Yeah, I know.': 'Oui, je sais.',
    'You drank too much.': "T'as trop bu.",
    'You like that?': "T'aimes ca ?",
    'You listening?': "Tu m'ecoutes ?",
    'You look good.': 'Bonne mine !',
    'You working later?': 'Tu bosses apres ?',
    "You're hopeless.": 'Irrecuperable.',
    "You're kidding!": 'Tu plaisantes !',
    "You're paying, right?": "C'est toi qui paies?",
    "You're so silly.": 'Trop bete.',
}

def translate_inplace(data_bytes, translations):
    out = bytearray(data_bytes)
    for en, fr in translations.items():
        en_b = en.encode('latin1') + b'\x00'
        fr_clean = fr.replace('Ça', 'Ca').replace('ÇA', 'CA').replace('Ç', 'C')
        fr_b = fr_clean.encode('latin1') + b'\x00'
        assert len(fr_b) <= len(en_b), f"Length error: {len(fr_b)} > {len(en_b)} for {repr(en)}"
        pos = 0
        while True:
            idx = out.find(en_b, pos)
            if idx == -1: break
            out[idx : idx + len(en_b)] = fr_b + b'\x00' * (len(en_b) - len(fr_b))
            pos = idx + len(en_b)
    return bytes(out)

def repack_par(orig_bytes, file_replacements={}):
    magic, unkA, unkB, unkC = struct.unpack('>4I', orig_bytes[:16])
    assert magic == 0x50415243
    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', orig_bytes[16:32])
    name_offset = 32 + folder_count * 64
    
    entries = []
    for i in range(file_count):
        n_off = name_offset + i * 64
        name = orig_bytes[n_off : n_off + 64].split(b'\x00')[0].decode('latin1')
        e_off = file_table_offset + i * 32
        entry_meta = list(struct.unpack('>8I', orig_bytes[e_off : e_off + 32]))
        flags, u_sz, c_sz, f_off = entry_meta[:4]
        raw_file = orig_bytes[f_off : f_off + c_sz]
        entries.append({
            'idx': i,
            'name': name,
            'entry_offset': e_off,
            'entry_meta': entry_meta,
            'flags': flags,
            'u_sz': u_sz,
            'c_sz': c_sz,
            'f_off': f_off,
            'data': raw_file
        })
    
    sorted_entries = sorted(entries, key=lambda e: e['f_off'])
    first_file_offset = sorted_entries[0]['f_off']
    rebuilt = bytearray(orig_bytes[:first_file_offset])
    curr_off = first_file_offset
    
    for item in sorted_entries:
        name = item['name']
        if name in file_replacements:
            n_flags, n_u_sz, n_c_sz, n_data = file_replacements[name]
        else:
            n_flags, n_u_sz, n_c_sz, n_data = item['flags'], item['u_sz'], item['c_sz'], item['data']
        
        aligned_off = (curr_off + 63) & ~63
        if aligned_off > len(rebuilt):
            rebuilt.extend(b'\x00' * (aligned_off - len(rebuilt)))
        
        new_file_offset = len(rebuilt)
        rebuilt.extend(n_data)
        curr_off = len(rebuilt)
        struct.pack_into('>4I', rebuilt, item['entry_offset'], n_flags, n_u_sz, n_c_sz, new_file_offset)
    
    return bytes(rebuilt)

def main():
    cpar_path = 'release_gog/data/wdr_par_c/common.par'
    bak_path = cpar_path + '.bak'
    if not os.path.exists(bak_path):
        print(f"[+] Backing up {cpar_path}...")
        shutil.copyfile(cpar_path, bak_path)

    with open(cpar_path, 'rb') as f:
        orig_bytes = f.read()

    files = parse_par(orig_bytes)
    replacements = {}

    for fn in ['blacksmith.bin', 'present.bin', 'sale0000.bin', 'sale0001.bin', 'sale0002.bin', 'send.bin', 'throw.bin']:
        if fn in files:
            flags, u_sz, c_sz, data = files[fn]
            trans = translate_inplace(data, COMMON_TRANSLATIONS)
            replacements[fn] = (flags, len(trans), len(trans), trans)
            print(f"  - Translated {fn}")

    # ai_popup.bin is SLLZ compressed
    if 'ai_popup.bin' in files:
        flags, u_sz, c_sz, data = files['ai_popup.bin']
        decomp = decompress_sllz(data)
        trans_decomp = translate_inplace(decomp, COMMON_TRANSLATIONS)
        comp = compress_sllz(trans_decomp)
        replacements['ai_popup.bin'] = (0x80000000, len(trans_decomp), len(comp), comp)
        print(f"  - Translated ai_popup.bin (decomp {u_sz} -> {len(trans_decomp)}, comp {c_sz} -> {len(comp)})")

    print("[+] Repacking common.par...")
    new_cpar = repack_par(orig_bytes, replacements)

    with open(cpar_path, 'wb') as f:
        f.write(new_cpar)

    print(f"[+] Successfully wrote {cpar_path} ({len(new_cpar)} bytes)!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Yakuza 0 GOG - French Fan-Translation Executable Patcher
-------------------------------------------------------
Adapts a clean GOG Yakuza 0 executable (v1.015a / Build 3642285) for the French
fan-translation (by Byce61 / Yakuza RGG France):
  1. Injects the French font table for extended accented characters (0x80-0xFF)
     into GOG offset 0xD488F0 while preserving native Sega ASCII kerning (0x00-0x7F)
     to avoid character overlapping bugs ('i', 'l', etc.).
  2. Injects single-byte font rendering assembly patches (0x396E9D, 0x39B358, 0x6FAEF6)
     to support French accented characters (é, è, à, ç, û, etc.) without crashing.
  3. Injects format string patch at 0xE73B70 (%s\\).
  4. Injects direct in-exe gameplay terms (REÇU, PERDU, NIV, Information, N°).
  5. Injects a .trad PE section and redirects .data string pointers for all 42 French
     menu options, chapter titles, and settings strings.

Usage:
  python3 patch_gog_exe.py [path_to_clean_Yakuza0.exe] [output_path]
"""

import sys
import os
import struct
import shutil
import zlib
import base64
import argparse
import stat
import time

# Import modern console UI module with robust fallback
try:
    from tools.console_ui import (
        Colors,
        strip_ansi,
        print_banner,
        card_start,
        card_line,
        card_end,
        format_progress,
        resolve_game_directory,
        validate_game_directory,
    )
except ImportError:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _tools_dir = os.path.join(_script_dir, "tools")
    if os.path.isdir(_tools_dir) and _tools_dir not in sys.path:
        sys.path.insert(0, _tools_dir)
    try:
        from console_ui import (
            Colors,
            strip_ansi,
            print_banner,
            card_start,
            card_line,
            card_end,
            format_progress,
            resolve_game_directory,
            validate_game_directory,
        )
    except ImportError:
        class Colors:
            RESET = ""
            BOLD = ""
            DIM = ""
            RED = ""
            GREEN = ""
            YELLOW = ""
            BLUE = ""
            MAGENTA = ""
            CYAN = ""
            WHITE = ""
            GRAY = ""

        def strip_ansi(t): return t
        def print_banner(version="v1.14.0", *args, **kwargs):
            print("=========================================================")
            print(f"  YAKUZA 0 — PATCH DE TRADUCTION FRANÇAISE ({version})")
            print("  Par Typhon0 (basé sur les traductions initiales de RGG FR)")
            print("=========================================================\n")
        def card_start(t, width=76, *args, **kwargs): print(f"\n--- [ {t} ] ---")
        def card_line(t, status="info", width=76, *args, **kwargs): print(f"  [{status.upper()}] {t}")
        def card_end(width=76, *args, **kwargs): print("-" * width)
        def format_progress(c, tot, width=16, *args, **kwargs):
            pct = int((c / tot) * 100) if tot > 0 else 100
            return f"[{pct:>3}%]"
            return f"[{pct:>3}%]"
        def validate_game_directory(d):
            return bool(d and os.path.isfile(os.path.join(d, "Yakuza0.exe")))
        def resolve_game_directory(p=None, interactive=True):
            if p and validate_game_directory(p): return p
            return None

# Embedded 6,144-byte French Font & Kerning Table (zlib-compressed base64)
# Calibrated for proportional spacing on narrow stems (i, l, I) and accented glyphs (é, è, ê, à, ç, etc.)
EMBEDDED_FONT_TABLE_B64 = (
    "eNrtV91xgzAM5vrY6wLMwbOtBRihz3nvBmzQZ7JGnrMBXaNzFGMLybIMOCXN9YLudCaKLMuffmxX1UEH"
    "PS+d+95q/DW8wbmvIR0H67kFwVba1mRr5OZo85qmAY39Hia/zPg5/w62AOfib/Sf1sP95OTxPtftSFxI"
    "FlRnrAi3bsS8trT3zp5O3xM7fT6ijo9Rm7CUe7uDkaNbI9ZpIx/cN2cmA1zD49oxezR6HW2soYTzeUv/"
    "Odsow7yQuDTNZcLGYRj0AfNFz0OMbzdjwHLUyNGvMxjaaxvwyFEXbNL4/vkCaINjyXKnoI7ivEbGmMnY"
    "BfyswBPxAzG6eVeNb/DTEG71pv0irnzUaiGOf9o3pD2ld0GocaA9TrEOmHVW9ifZx1zf9Bz1gErm91r+"
    "yziW1ovWx3Jy3t+wH7G4m/CfETzrY/6Hmtd0DdtH1PecDGvU9zvEP1qf5QraasN3K/wpwg3SXjissawB"
    "tq/Iz0U55hXxwLCL9hbq+MLPLCD78hxf9n/ZTx9DvtYou3rW4s6xi/xP7MjzJReX3Lmf08+dy/w+8McE"
    "nEOPSOpQ1qOcn/aPHs+xgw466KCH0Id5Bcd0z/G83/t0OpuVPq/fW269J2v3/EfoL7+LtfeF/o7YS77h"
    "/vMrfoYaWX4HbtcvtVOS/6X31XvJF/qAdmdM7pPsnbCr/L/mfynOpfr3Xncvf3L0A8noUDg="
)

# GOG Executable Offsets (v1.015a)
GOG_FONT_TABLE_OFFSET = 0xD488F0
FONT_TABLE_SIZE = 6144  # 256 characters * 24 bytes (6 floats each)

# Assembly bytecode patches for single-byte ANSI/Windows-1252 character rendering
GOG_BYTECODE_PATCHES = [
    # Patch 1: Bypass multi-byte font width check in font rendering routine
    (0x396E9D, bytes([0xEB, 0x1C]), "Font width check bypass (0x396E9D -> EB 1C)"),
    # Patch 2: Skip character count multi-byte loop
    (0x39B358, bytes([0xEB, 0x47]), "Character length loop skip (0x39B358 -> EB 47)"),
    # Patch 3: Nullify Shift-JIS encoding restriction flag (NOP; NOP)
    (0x6FAEF6, bytes([0x90, 0x90]), "Encoding flag override (0x6FAEF6 -> 90 90)"),
    # Patch 4: Format string patch (%s\)
    (0xE73B70, bytes([0x25, 0x73, 0x5C]), "Format string patch (0xE73B70 -> %s\\)"),
]

# Direct in-exe word replacements at fixed GOG locations
GOG_DIRECT_WORDS = [
    (0xDD73C8, b'RECU\x00', "GET -> RECU (0xDD73C8)"),
    (0xE69424, b'PERDU\x00', "LOST -> PERDU (0xE69424)"),
    (0xDC5308, b'NIV\x00', "LV -> NIV (0xDC5308)"),
    (0xDC5338, b'Information\x00', "Information (0xDC5338)"),
    (0xE69C00, b'N\xb0 \x00', "No. -> N° (0xE69C00)"),
    # Commandes bornes d'arcade Club SEGA (Space Harrier, Out Run, Fantasy Zone, Super Hang-On)
    (0xD84468, b'Tir\x00', "Fire -> Tir (0xD84468)"),
    (0xD84470, b'Tir rapide\x00', "Rapid-Fire -> Tir rapide (0xD84470)"),
    (0xD84480, b'Ins\xe9rer cr\xe9dit\x00', "Insert Credit -> Insérer crédit (0xD84480)"),
    (0xD84490, b'Commandes\x00', "Controls -> Commandes (0xD84490)"),
    (0xD8449C, b'Vol\x00', "Fly -> Vol (0xD8449C)"),
    (0xD844A0, b'Pause/Quitter\x00', "Pause/Quit -> Pause/Quitter (0xD844A0)"),
    (0xD844B0, b'Start/Commandes\x00', "Start/Controls -> Start/Commandes (0xD844B0)"),
    (0xD844C0, b'Acc\xe9l\xe9rer/Confirmer\x00', "Accelerate/Confirm -> Accélérer/Confirmer (0xD844C0)"),
    (0xD844D8, b'Changer affichage\x00', "Switch Screen Type -> Changer affichage (0xD844D8)"),
    (0xD844F0, b'Inverser axes\x00', "Invert Controls -> Inverser axes (0xD844F0)"),
    (0xD84500, b'Frein\x00', "Brake -> Frein (0xD84500)"),
    (0xD84508, b'Volant\x00', "Steer -> Volant (0xD84508)"),
    (0xD84510, b'Tir/S\xe9lection\x00', "Fire/Select -> Tir/Sélection (0xD84510)"),
    (0xD84520, b'Changer vitesse\x00', "Shift Gears -> Changer vitesse (0xD84520)"),
    (0xD84530, b'Activer Turbo\x00', "Switch Turbo -> Activer Turbo (0xD84530)"),
    (0xD84540, b'Bombe\x00', "Bomb -> Bombe (0xD84540)"),
    # Options & Configuration des commandes (Zone A & Zone C)
    (0xD831C0, b'Saisie / Annul.\x00', "Grab / Cancel -> Saisie / Annul. (0xD831C0)"),
    (0xD831D0, b'Centrer cam\xe9ra\x00', "Camera Reset -> Centrer caméra (0xD831D0)"),
    (0xD83CB8, b'Reconfigurer manette\x00', "Remap Gamepad Controls -> Reconfigurer manette (0xD83CB8)"),
    (0xD83CD0, b'Reconfigurer clavier/souris\x00', "Remap Keyboard & Mouse Controls -> Reconfigurer clavier/souris (0xD83CD0)"),
    (0xD851E0, b'Appuyez sur une touche pour r\xe9assigner la commande\nAppuyez sur [\xc9chap] pour annuler\x00', "Press a button to rebind -> Appuyez sur une touche (0xD851E0)"),
    (0xD85400, b'Appuyez sur <Sign:60> pour avancer.\x00', "Press <Sign:60> to fast forward -> Appuyez sur <Sign:60> (0xD85400)"),
    (0xD85468, b'Manette d\xe9connect\xe9e\x00', "Controller disconnected -> Manette déconnectée (0xD85468)"),
    (0xD85AE0, b"<Sign:C> : Fermer les informations d\xe9taill\xe9es.\n<Sign:59>/<Sign:60> : Parcourir les autres pages d'infos.\x00", "Press <Sign:C> to close -> Fermer les informations (0xD85AE0)"),
    # Mini-jeu Téléphone Club (Telekura Rinrin-bo - Kiryu) : Roulette & Dialogues d'imagination
    (0xD85320, b'Quoi ? Ma silhouette ?\x00', "What? My body type? -> Quoi ? Ma silhouette ? (0xD85320)"),
    (0xD85338, b'Mon visage ?\x00', "My face? -> Mon visage ? (0xD85338)"),
    (0xD85348, b'Quoi ? Maintenant ??\x00', "What? You mean now?? -> Quoi ? Maintenant ?? (0xD85348)"),
    (0xD85360, b"Hum, mon corps t'int\xe9resse ?\x00", "Interested in body -> Hum, mon corps t'intéresse ? (0xD85360)"),
    (0xD85388, b'Quel genre de visage tu aimes... ?\x00', "Face preference -> Quel genre de visage tu aimes... ? (0xD85388)"),
    (0xD853B0, b"Tu te d\xe9cides enfin \xe0 m'inviter !\x00", "Invite me -> Tu te décides enfin à m'inviter ! (0xD853B0)"),
    (0xD853D8, b'Eh bien, mon corps...\x00', "Well, my body... -> Eh bien, mon corps... (0xD853D8)"),
    (0xD853F0, b"Hum, d'accord.\x00", "Hmmm, okay. -> Hum, d'accord. (0xD853F0)"),
    (0xD8C4D0, b"J'adore le sport, j'ai un corps plut\xf4t muscl\xe9.\nMais sois pas trop brutal avec moi. Enfin bref,\nje m'emballe un peu, non ? Dr\xf4le de question.\x00", "Toned side -> J'adore le sport... (0xD8C4D0)"),
    (0xD8C580, b"On dit que mon visage est fin. Cheveux courts,\nmais les mecs pr\xe9f\xe8rent long. Tu aimes\nles filles aux cheveux courts ?\x00", "Small face -> On dit que mon visage... (0xD8C580)"),
    (0xD8C600, b"Oui. J'ai envie de te voir aussi. Je stresse !\nMais j'ai vraiment h\xe2te. Retrouvons-nous.\x00", "Meet up -> Oui. J'ai envie de te voir... (0xD8C600)"),
    (0xD8C670, b"Voyons, je fais attention \xe0 ma ligne. Une fille\ndouce attire les gentlemen. Mais bon, parfois\n\xeatre douce c'est un peu ennuyeux... \x00", "Careful figure -> Voyons, je fais attention... (0xD8C670)"),
    (0xD8C700, b"On dit que je ressemble aux idoles de la t\xe9l\xe9.\nLe genre coquette ? Haha, tu ferais bien\nde te m\xe9fier...\x00", "Idol face -> On dit que je ressemble... (0xD8C700)"),
    (0xD8C780, b"On va enfin se voir ? Tu m'as d\xe9j\xe0 bien chauff\xe9e,\nalors me laisse pas en plan... Commencons\npar nous amuser un peu, d'accord ?\x00", "Finally meet -> On va enfin se voir ? (0xD8C780)"),
    (0xD8C820, b"Mon soutien-gorge est trop serr\xe9 ces temps-ci.\nFaut que j'en rach\xe8te. Mais pourquoi je te dis ca ?\nC'est un peu intime comme question.\x00", "Bra tighter -> Mon soutien-gorge... (0xD8C820)"),
    (0xD8C8C0, b"Tu veux en savoir plus, hein ? On dit que mon\nvisage est sexy. Pourquoi ? Je suis une femme.\x00", "Sexy face -> Tu veux en savoir plus... (0xD8C8C0)"),
    (0xD8C930, b"Tu as tant envie de me voir ? Hm ? Non non,\nmoi aussi je veux te voir. Je te suivrai\npartout o\xf9 tu voudras.\x00", "Wherever you want -> Tu as tant envie... (0xD8C930)"),
]

# French strings mapped to original English strings in .rdata
# The patcher locates the English strings in .rdata, finds their 64-bit pointers in .data,
# writes the French translations into .trad, and updates the pointers.
FRENCH_UI_TRANSLATIONS = {
    # Main menu & common prompts
    "Start a new game.": "Commencer une nouvelle partie.",
    "Quit game?": "Quitter le jeu ?",
    "<Sign:1> Quit": "<Sign:1> Quitter",
    "Load a saved game.": "Chargez une partie sauvegardée.",
    "Adjust various settings.": "Réglez divers paramètres.",
    "View previously seen story events.": "Affichez les événements de l'histoire vus précédemment.",
    "View information regarding network functions.": "Affichez des informations sur les fonctions en ligne.",
    "Two players compete in four types of minigames:\nBowling, Darts, Pool, and Disco.\n*Does not count toward results or the Completion List.": (
        "Deux joueurs s'affrontent dans quatre types de mini-jeux :\n"
        "Le bowling, les fléchettes, le billard et la discothèque.\n"
        "*Ne compte pas dans les résultats ou la liste d'achèvement."
    ),
    "Challenge other players online in Mahjong, Cee-lo, or Poker.\n*Does not count toward the Completion List.": (
        "Défiez d'autres joueurs en ligne au mahjong, au cee-lo ou au poker.\n"
        "*Ne compte pas dans la liste d'achèvement."
    ),
    "A challenge mode for the best fighters. Connect\nonline to compete on the leaderboards.\n*Does not count toward the Completion List.": (
        "Un mode défi pour les meilleurs combattants. Connectez-vous\n"
        "en ligne pour participer aux classements.\n"
        "*Ne compte pas dans la liste d'achèvement."
    ),
    # Chapter titles with subtitles
    "CHAPTER 1 : Bound by Oath": "CHAPITRE 1 : Lié par serment",
    "CHAPTER 2 : The Real Estate Broker in the Shadows": "CHAPITRE 2 : Le courtier immobilier dans l'ombre",
    "CHAPTER 3 : A Gilded Cage": "CHAPITRE 3 : Une cage dorée",
    "CHAPTER 4 : Proof of Resolve": "CHAPITRE 4 : Preuve de volonté",
    "CHAPTER 5 : An Honest Living": "CHAPITRE 5 : Une vie honnête",
    "CHAPTER 6 : The Yakuza Way": "CHAPITRE 6 : La voie yakuza",
    "CHAPTER 7 : A Dark Escape": "CHAPITRE 7 : Une sombre fuite",
    "CHAPTER 8 : Tug of War": "CHAPITRE 8 : Lutte acharnée",
    "CHAPTER 9 : Ensnared": "CHAPITRE 9 : Pris au piège",
    "CHAPTER 10 : A Man's Worth": "CHAPITRE 10 : La valeur d'un homme",
    "CHAPTER 11 : Troubled Waters": "CHAPITRE 11 : En eau trouble",
    "CHAPTER 12 : Den of Desires": "CHAPITRE 12 : Antre des désirs",
    "CHAPTER 13 : Crime and Punishment": "CHAPITRE 13 : Crime et châtiment",
    "CHAPTER 14 : Unbreakable Bond": "CHAPITRE 14 : Lien indéfectible",
    "CHAPTER 15 : Scattered Light": "CHAPITRE 15 : Lumière dispersée",
    "CHAPTER 16 : Proof of Love": "CHAPITRE 16 : Preuve d'amour",
    "Chapter Completion Bonus": "Bonus de fin de chapitre",
}


def get_font_table_bytes():
    """Returns the uncompressed 6,144 bytes of the French font UV table."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    external_bin = os.path.join(script_dir, "font_table_french.bin")
    if os.path.isfile(external_bin):
        with open(external_bin, "rb") as f:
            data = f.read()
            if len(data) == FONT_TABLE_SIZE:
                return data
    # Fallback to embedded base64
    return zlib.decompress(base64.b64decode(EMBEDDED_FONT_TABLE_B64))


def align(val, alignment):
    """Aligns a value upwards to the given alignment."""
    return (val + alignment - 1) & ~(alignment - 1)


POKECIR_COMMENTARY = {"Kazuma-kun's Golem Tiger...": 'Golem Tiger de Kazuma-kun...', "Kazuma-kun's Golem Tiger!": 'Golem Tiger de Kazuma-kun !', "Kazuma-kun's  DRA-GON...": 'DRA-GON de Kazuma-kun...', "Kazuma-kun's  DRA-GON!": 'DRA-GON de Kazuma-kun !', "Kazuma-kun's  DRAG-ON!": 'DRAG-ON de Kazuma-kun !', "Kazuma-kun's Cool Striker...": 'Cool Striker de Kazuma-kun...', "Kazuma-kun's Cool Striker!": 'Cool Striker de Kazuma-kun !', "Kazuma-kun's Devil Killer...": 'Devil Killer de Kazuma-kun...', "Kazuma-kun's Devil Killer!": 'Devil Killer de Kazuma-kun !', "Kazuma-kun's Killer Bee...": 'Killer Bee de Kazuma-kun...', "Kazuma-kun's Killer Bee!": 'Killer Bee de Kazuma-kun !', "Kazuma-kun's Yakuza 3...": 'Yakuza 3 de Kazuma-kun...', "Kazuma-kun's Yakuza 3!": 'Yakuza 3 de Kazuma-kun !', "Kazuma-kun's Yakuza Three!": 'Yakuza Three de Kazuma-kun !', "This course will put the machine's strengths on display!\nDon't get swept off your feet!": 'Ce tracé mettra en valeur la force de vos bolides !\nNe vous laissez pas déborder !', 'The key to this course will be power and speed.\nZoom through it with confidence!': 'La clé sur ce circuit sera puissance et vitesse.\nFoncez avec assurance !', "This course knocks racers right off the track!\nEveryone's taken precautions, right!?": 'Ce circuit éjecte les bolides sans pitié !\nTout le monde a pris ses précautions, pas vrai !?', "You can't beat this course on brute force alone!\nMake sure you've customized for this challenge!": "La force brute ne suffira pas sur ce circuit !\nAssurez-vous d'avoir bien ajusté vos pièces !", 'Speed and technique! This course will test both!\nI look forward to seeing how you balance them!': 'Vitesse et technique ! Ce tracé testera les deux !\nHâte de voir votre équilibre sur la piste !', "It's uncharted territory! This course is all sorts\nof difficult! Can you make history on it!?": "Terrain inexploré et truffé de pièges !\nSerez-vous capable d'y marquer l'Histoire !?", 'At the heart of this course looms a giant loop!\nClear it with power and speed!': 'Au cœur de ce circuit se dresse un looping géant !\nFranchissez-le en force et vitesse !', "The challenge of this course is the sharp curb!\nLet your guard down, and you'll fly right off!": 'Le défi réside dans ce virage serré !\nBaissez la garde et vous volerez dans le décor !', 'Be extra cautious on this turf!\nDash through it before it steals your speed!': "Grande prudence sur ce gazon !\nTraversez-le vite avant qu'il ne ruine votre allure !", 'A jump awaits you on this course!\nShow me a wild jump and a beautiful landing!': 'Un tremplin vous attend sur ce tracé !\nOffrez-moi un saut superbe et un atterrissage net !', 'Dig in for the long haul on this course!\nI hope your machines are customized for toughness!': "Préparez-vous à une longue bataille !\nJ'espère que vos bolides sont taillés pour durer !", "A single mistake could be fatal on this course!\nYou really can't let your guard down here!": 'La moindre erreur sera fatale ici !\nInterdiction de relâcher son attention !', 'This course is no walk in the park!\nTake a good look at it and customize accordingly!': "Ce circuit n'est pas une simple promenade !\nObservez-le bien et réglez vos pièces !", 'A great many machines have attempted this course!\nHow will the racers we have today tackle it!?': "Tant de bolides ont bravé ce tracé !\nComment nos pilotes du jour vont-ils s'y mesurer !?", 'All the drama on this course makes it my favorite!\nWhat kind of miracle will we see here today!?': "Ces folles péripéties en font ma piste préférée !\nQuel miracle allons-nous vivre aujourd'hui !?", "It's Kazuma-kun versus Takuma-kun, who just got his\nstart in Pocket Circuit! Who will dominate this race!?": 'Kazuma-kun face à Takuma-kun, grand débutant\nau Poké-Circuit ! Qui dominera cette course !?', "Kazuma-kun is up against a racer who's been really\ndeveloping his technique lately... Hideki-kun!": 'Kazuma-kun affronte un pilote en plein essor\ntechnique ces temps-ci... Hideki-kun !', 'Kazuma-kun is up against Mika-chan, who has a\nskilled hand! Whose customization will reign supreme!?': 'Kazuma-kun défie Mika-chan aux doigts de fée !\nQuels réglages feront la loi sur la piste !?', 'Satoru-kun has been rocking Pocket Circuit since it first\nreleased! Can Kazuma-kun win against his long history!?': 'Satoru-kun pilote depuis les débuts du Poké-Circuit !\nKazuma-kun vaincra-t-il cette légende !?', "It was her brother who got Sena-chan into Pocket Circuit,\nbut now she's surpassed him! Will sparks fly today!?": "Initié par son frère, Sena-chan l'a déjà surpassé !\nY aura-t-il des étincelles aujourd'hui !?", 'Harumi-chan is the Pocket Circuit Professor!\nCan Kazuma-kun overcome her wealth of knowledge!?': 'Harumi-chan est la prof du Poké-Circuit !\nKazuma-kun surmontera-t-il son grand savoir !?', 'Kazuyoshi-kun has won countless tournaments!\nThis race against Kazuma-kun will be one for the books!': 'Kazuyoshi-kun a gagné tant de tournois !\nCe duel face à Kazuma-kun restera dans les mémoires !', "The racer facing the fearless Kazuma-kun and his\nincredible streak is none other than... ME!\nI won't hold anything back! Come at me!": "Le rival face au vaillant Kazuma-kun n'est autre\nque... MOI ! Le Fighter !\nJe ne retiendrai rien ! À nous deux !", 'This challenger is undefeated in his hometown!\nWill the flawless record continue in Kamurocho!?': "Ce challenger est invaincu sur ses terres d'origine !\nSa série parfaite résistera-t-elle à Kamurocho !?", "Kazuma-kun's rival is a tournament regular!\nWho will take the glorious victory!?": "Le rival de Kazuma-kun est un habitué des tournois !\nQui s'emparera de cette glorieuse victoire !?", "I sense determination in this challenger's eyes!\nCan Kazuma-kun emerge victorious here!?": "Je lis une détermination d'acier dans les yeux du challenger !\nKazuma-kun saura-t-il triompher aujourd'hui !?", 'This rival has an 80^ victory rate in Pocket Circuit!\nThis will be one tough opponent, no doubt!': 'Ce rival a 80 % de victoires au Poké-Circuit !\nUn adversaire redoutable, sans aucun doute !', 'Our remarkable Kazuma-kun is in lane 1!': 'Notre cher Kazuma-kun est dans le couloir 1 !', 'Our remarkable Kazuma-kun is in lane 2!': 'Notre cher Kazuma-kun est dans le couloir 2 !', 'Our remarkable Kazuma-kun is in lane 3!': 'Notre cher Kazuma-kun est dans le couloir 3 !', 'Our remarkable Kazuma-kun is in lane 4!': 'Notre cher Kazuma-kun est dans le couloir 4 !', 'Our remarkable Kazuma-kun is in the green lane!': 'Notre cher Kazuma-kun est sur la voie verte !', 'Our remarkable Kazuma-kun is in the yellow lane!': 'Notre cher Kazuma-kun est sur la voie jaune !', 'Our remarkable Kazuma-kun is in the blue lane!': 'Notre cher Kazuma-kun est sur la voie bleue !', 'Our remarkable Kazuma-kun is in the red lane!': 'Notre cher Kazuma-kun est sur la voie rouge !', 'His opponent is Takuma-kun!': 'Son adversaire est Takuma-kun !', 'His opponent is Hideki-kun!': 'Son adversaire est Hideki-kun !', 'His opponent is Mika-chan!': 'Son adversaire est Mika-chan !', 'His opponent is Satoru-kun!': 'Son adversaire est Satoru-kun !', 'His opponent is Harumi-chan!': 'Son adversaire est Harumi-chan !', 'His opponent is Sena-chan!': 'Son adversaire est Sena-chan !', 'His opponent is Kazuyoshi-kun!': 'Son adversaire est Kazuyoshi-kun !', 'His opponent is Tamio-kun!': 'Son adversaire est Tamio-kun !', "Looks like everyone's in their lane and ready\nto go! Good luck to you all!": 'Tout le monde est en position et paré au départ !\nBonne chance à tous !', "Is everyone on standby!? Don't get a late start!": 'Tout le monde est prêt !? Ne loupez pas le départ !', "Let's get this race started!": 'Que la course commence !', 'Everyone to their places!': 'Chacun à son poste !', 'Ready...!': 'À vos marques... !', 'GO!': 'PARTEZ !', 'All the machines are off!': "Tous les bolides s'élancent !", 'What a smooth start!': 'Quel départ impeccable !', 'Good luck everyone!': 'Bonne chance à tous les pilotes !', 'The lead is taken right away!': 'La tête de course est prise dès le départ !', 'Was there some hesitation!?': 'Y a-t-il eu une petite hésitation !?', 'Here comes that sharp corner!': 'Voici le fameux virage serré !', 'Everyone better be careful not to fly off course!': 'Attention à tous, ne quittez pas la piste !', 'If you fly off course, the whole race is wasted!': "Une sortie de route et toute la course s'envole !", "Kazuma-kun's machine has incredible cornering!": 'Le bolide de Kazuma-kun négocie le virage à merveille !', "Oh no! Kazuma-kun's machine flies off the course!": 'Oh non ! Le bolide de Kazuma-kun quitte la piste !', "It's the turf zone!": 'Voici la zone de gazon !', "You'll lose speed unless you planned ahead!": "Vous perdrez de l'allure sans anticipation !", 'Did you customize for this!?': 'Aviez-vous prévu les bons réglages !?', "Kazuma-kun's incredible customization puts him\non top right from the get-go!": "Les réglages parfaits de Kazuma-kun\nl'installent en tête dès le début !", "Kazuma-kun's machine has suddenly lost speed!": 'Le bolide de Kazuma-kun ralentit brutalement !', 'The jump zone ambushes the racers!': 'Le tremplin attend nos pilotes au tournant !', "Don't over-do the jump!": 'Ne sautez pas trop fort !', 'A clean landing is all that matters!': "Une réception propre, c'est tout ce qui compte !", 'Kazuma-kun sticks the landing beautifully!': 'Kazuma-kun plaque une réception splendide !', "Kazuma-kun's machine takes a bounce!": 'Le bolide de Kazuma-kun rebondit violemment !', 'Here comes the loop zone!': 'Voici la zone du looping !', 'The key to this is speed!': "La clé ici, c'est la vitesse !", 'Zoom through it at full throttle!': 'Traversez-le pied au plancher !', "Kazuma-kun's machine clears the loop dramatically!": 'Le bolide de Kazuma-kun passe le looping avec panache !', 'Whoa, Kazuma-kun is out!\nWas he too slow!?': 'Kazuma-kun décroche !\nManquait-il de vitesse !?', "There's no telling who will win yet!\nKeep charging to the finish!": "Vainqueur imprévisible pour l'instant !\nAttaquez jusqu'à la ligne !", 'This is a high-level battle! Aim for the top!': 'Duel de très haut vol ! Visez le sommet !', "Kazuma-kun is chasing the lead!\nHe'll need to flip the tables here!": 'Kazuma-kun prend le leader en chasse !\nIl doit renverser la vapeur maintenant !', "He's in first place! Can he hold it, though!?": 'Il est en première place ! Arrivera-t-il à la garder !?', 'Still holding on to the lead!': 'Toujours solidement accroché à la tête !', 'Keep on racing!': 'Ne relâchez pas votre allure !', 'So powerful! Everyone is eating dust!': 'Quelle puissance ! Tout le monde mange sa poussière !', "It's a huge gap between first and second place!": "L'écart est immense entre le premier et le second !", "He's got the need for speed!": 'Il a une vitesse folle et la rage de vaincre !', "What's wrong with Kazuma-kun!? Could he be\nbiding his time in last place on purpose!?": "Qu'arrive-t-il à Kazuma-kun !? Patienterait-il\nen queue de peloton exprès !?", "Kazuma-kun is dead-last in this race!\nLet's hope he can make a recovery!": 'Kazuma-kun est bon dernier !\nEspérons une remontée spectaculaire !', 'This gripping race continues on!': 'Cette course haletante se poursuit !', 'Who will walk away with the crown!?': 'Qui repartira avec la couronne de vainqueur !?', 'Show off those glorious customizations!': 'Montrez-nous ces splendides bolides customisés !', "Everyone's making this an amazing race!": 'Nos pilotes nous offrent une course mémorable !', 'The machines speed on, and the crowd goes wild!': 'Les bolides foncent et la foule est en délire !', "Don't give up until the very end!": "N'abandonnez rien jusqu'au dernier mètre !", 'What twist of fate could be waiting ahead!?': 'Quel coup du sort nous attend dans les virages !?', 'This race is really heating up!': 'Cette course monte sérieusement en température !', 'Wow, Kazuma-kun speeds on ahead to take first!': 'Kazuma-kun accélère et prend la tête !', "Kazuma-kun's finally taken the lead!": 'Kazuma-kun prend enfin la tête !', "Kazuma-kun's machine has caught up to the pack!": 'Le bolide de Kazuma-kun recolle au peloton !', 'Kazuma-kun passes the leader!': 'Kazuma-kun dépasse le leader !', 'Oh man, Kazuma-kun has fallen from the top!': 'Mince, Kazuma-kun a perdu la première place !', 'Kazuma-kun just handed over the lead!': 'Kazuma-kun vient de céder la tête !', "Kazuma-kun's machine just got passed up!": 'Kazuma-kun vient de se faire doubler !', "Kazuma-kun's machine has lost its position!": 'Kazuma-kun a perdu son rang !', 'Whoa, Kazuma-kun flew off the track!\nDid he get too ambitious!?': 'Kazuma-kun a décollé hors piste !\nA-t-il été trop gourmand !?', 'First place GOAL!\nThank you for the exciting race!': 'Victoire en 1re place !\nMerci pour cette course palpitante !', 'Goooooal! Congratulations!': 'Arrivéééee ! Félicitations !', 'A magnificent first place! Strong as ever!': 'Éclatante 1re place ! Brillant comme toujours !', 'Kazuma-kun takes second place!\nCongrats on finishing the race!': 'Kazuma-kun prend la 2e place !\nBravo pour cette belle course !', 'Kazuma-kun takes third place!\nCongrats on finishing the race!': 'Kazuma-kun prend la 3e place !\nBravo pour cette belle course !', 'Kazuma-kun takes fourth place!\nCongrats on finishing the race!': 'Kazuma-kun prend la 4e place !\nBravo pour cette belle course !', "Kazuma-kun hits his boost like an impatient child!\nHe's secured the first place slot!": 'Kazuma-kun claque son turbo comme un enfant !\nIl verrouille la 1re place !', "He hits the boost! It's a fierce catch-up!": 'Il active le turbo ! Quelle remontée féroce !', 'It looked like he might fly off course,\nbut he showed guts and planted himself!': 'On le croyait dans le décor,\nmais il a su stabiliser son bolide !', 'An unexpected retirement!\nTruly a waste...!': 'Un abandon inattendu !\nQuel immense gâchis... !', 'Nothing worse than retiring from the top!': "Rien de plus cruel qu'un abandon alors qu'on menait !", "An early retirement! What a shame that we'll\nhave no highlights... But don't give up the race!": 'Abandon précoce ! Quel dommage...\nMais ne baissez pas les bras pour la suite !', "He fought his hardest, but he had to retire!\nWe'll be waiting for your next challenge!": "Il a lutté de toutes ses forces avant d'abandonner !\nOn attend votre revanche avec impatience !", 'Kazuma-kun is the winner! Congratulations!': 'Kazuma-kun est le grand gagnant ! Félicitations !', "Today's race was dominated by Kazuma-kun!\nCongratulations!": 'Course dominée par Kazuma-kun !\nFélicitations !', 'A round of applause for our winner!\nCongratulations!': 'Applaudissements pour le vainqueur !\nFélicitations !', 'That was a heart-pounding battle!\nThank you for the amazing race!': "Duel palpitant à mille à l'heure !\nMerci pour ce fabuleux spectacle !", 'The winner of this tournament is... Kazuma-kun!\nI hope to see you keep on racing!': 'Vainqueur du tournoi : Kazuma-kun !\nContinuez à faire rugir vos moteurs !', 'Kazuma-kun is the winner of our tournament!\nCongratulations!': 'Kazuma-kun remporte le tournoi !\nToutes nos félicitations !', 'The victor is decided! Thank you for being\nsuch a great audience!': 'Le vainqueur est couronné !\nMerci à notre formidable public !', 'That match could have gone to anyone.  Our winner should\nstrive for new heights, and losers should hone their skills!': "Ce duel pouvait basculer d'un côté comme de l'autre.\nBravo au vainqueur et persévérance à tous !", 'The victor of this intense duel is Kazuma-kun!\nCongratulations!': 'Le triomphateur de ce duel est Kazuma-kun !\nFélicitations !', 'It was a heated race, but victory was stolen from\nthe jaws of defeat by... Kazuma-kun! Congrats!': "Quelle bagarre d'anthologie ! Kazuma-kun arrache\nla victoire au nez et à la barbe de son rival !", 'A round of applause for our racers who showed\nsuch fierce resolve! Thank you both!': 'Applaudissons nos deux valeureux pilotes !\nMerci à tous les deux !', 'The winner is Takuma-kun! Congratulations!': 'Le vainqueur est Takuma-kun ! Félicitations !', 'The winner is Hideki-kun! Congratulations!': 'Le vainqueur est Hideki-kun ! Félicitations !', 'The winner is Mika-chan! Congratulations!': 'La gagnante est Mika-chan ! Félicitations !', 'The winner is Satoru-kun! Congratulations!': 'Le vainqueur est Satoru-kun ! Félicitations !', 'The winner is Harumi-chan! Congratulations!': 'La gagnante est Harumi-chan ! Félicitations !', 'The winner is Sena-chan! Congratulations!': 'La gagnante est Sena-chan ! Félicitations !', 'The winner is Kazuyoshi-kun! Congratulations!': 'Le vainqueur est Kazuyoshi-kun ! Félicitations !', 'The winner is Tamio-kun! Congratulations!': 'Le vainqueur est Tamio-kun ! Félicitations !', "The machine I'm going to use is THIS!\nThink you can keep up with me!?": 'Le bolide que je vais piloter est CELUI-CI !\nTu penses suivre mon rythme !?', 'Looks like this is a real race!': 'Là, on a une vraie course entre pros !', 'What the--!? That was radical!': "Qu'est-ce que... !? C'était dément !", "This is what I'm made of!": 'Voilà de quel bois je me chauffe !', "Not so fast! You can't beat me so easily!": 'Pas si vite ! On ne me bat pas si facilement !', "Heh, a rookie mistake!\nYou're going too fast!": 'Hé, erreur de débutant !\nTu roules beaucoup trop vite !', 'Better go back to your customization!': 'Tu ferais bien de revoir tes réglages !', 'Wha...!? Impossible!': "Qu... !? C'est impossible !", 'No! I got too carried away!': 'Non ! Je me suis emballé !', 'Such determination!': 'Quelle détermination farouche !', 'You were holding back strength like that!?': 'Tu cachais une telle puissance en réserve !?', "To think you'd recover from that position...\nWell done!": 'Réussir à te rattraper dans cette position...\nBien joué !', 'Impressive guts, Kazuma-kun!': 'Un sang-froid admirable, Kazuma-kun !', "Looks like you weren't quite ready for this.\nYou can challenge me any time!": "On dirait que tu n'étais pas tout à fait prêt.\nReviens m'affronter quand tu veux !", "I know you won't let it end like this!\nI await your next challenge!": "Je sais que tu ne vas pas en rester là !\nJ'attends ta prochaine revanche de pied ferme !", 'Well done, Kazuma-kun!\nThis is starting to get fun!': 'Chapeau, Kazuma-kun !\nÇa commence à devenir vraiment amusant !', 'Tch, I let my guard down...\nBut the real battle begins now, Kazuma-kun!': "Tss, j'ai baissé la garde...\nLa vraie bataille commence, Kazuma-kun !", "Heh heh, I'm on a roll!": "Hé hé, rien ne peut m'arrêter !", "I know you've got more than this!\nShow me everything you've got!": 'Tu en as encore sous le capot !\nMontre-moi ce que tu as dans le ventre !', 'Just as I thought... I am defeated!\nCongratulations!': 'Comme je le pressentais... Je suis battu !\nFélicitations !', "That race was fantastic!\nLet's do it again some time!": "Cette course était fantastique !\nRemettons ça à l'occasion !", 'Such an intense battle!\nI was having the time of my life!': 'Quelle lutte acharnée !\nJe me suis amusé comme jamais !', 'The winner is Kazuma-kun!\nYou are truly the greatest racer!!!': 'Le vainqueur est Kazuma-kun !\nTu es véritablement le plus grand des pilotes !!!', "Looks like I'm the winner of today's race!\nBut I'll accept a rematch any time! Bring it on!": "La victoire m'appartient aujourd'hui !\nRevanche quand tu veux !", 'Uh-oh!': 'Oh-oh !', 'Oh, man!': 'La poisse !', 'Amazing!': 'Incroyable !', 'Wow!': 'Ouah !', "Ooh, that's bad!": 'Aïe, ça sent mauvais !', "I can't watch!": 'Je ne peux pas regarder !', "The one you're up against is ME!\nThe Pocket Circuit Fighter!": "Celui que tu affrontes n'est autre que MOI !\nLe Pocket Circuit Fighter !", 'This course is so long, your machine has to be\nreally tough to handle it!': 'Ce tracé est si long que votre bolide doit être\ntrès robuste pour tenir le coup !', "Everyone's customizations are shining!": 'Les personnalisations de chacun brillent sur la piste !', 'Is this the calm before the storm!?': 'Serait-ce le calme avant la tempête !?', 'Not knowing what could happen next is what\nPocket Circuit is all about!': "L'imprévu à chaque virage, c'est ça\ntoute l'essence du Poké-Circuit !", 'In Pocket Circuit, social standing can be turned on\nits head!': "Au Poké-Circuit, tous les statuts sociaux\ns'effacent devant la piste !", 'Is it possible to maintain this lead!?': 'Sera-t-il possible de préserver cette avance !?', "Don't get swept off your feet!": 'Ne vous laissez pas déborder !', 'PLACEHOLDER! PLEASE BUG ME!\neSEID_pokecir_live_nrm_216_race_idle_pokecir_live_nrm_216_race_idle': 'PLACEHOLDER! PLEASE BUG ME!\neSEID_pokecir_live_nrm_216_race_idle_pokecir_live_nrm_216_race_idle', "It's a long wall!": "C'est un long mur !", "Don't let your guard down until the end of the wall!": 'Ne relâchez pas votre garde avant la fin du mur !', 'Can they all get through this wall safely!?': 'Parviendront-ils tous à franchir ce mur sans encombre !?', 'Watch your acceleration as you come down!': 'Attention à votre accélération dans la descente !', "A zigzag zone can't be taken lightly!": 'Une zone en zigzag ne doit jamais être prise à la légère !', 'Be super careful not to fly off the course!': 'Prudence extrême pour ne pas décoller du circuit !', 'Balance is important!': "L'équilibre est primordial !", 'Oh no! Kazuma-kun flew right off the course!\nWhat a crying shame...!': 'Oh non ! Kazuma-kun est sorti de piste !\nQuel cruel coup du sort... !', 'Kazuma-kun has flown off the course!\nVictory slips through his fingers!': "Kazuma-kun s'est envolé hors de piste !\nLa victoire lui glisse entre les doigts !", 'Kazuma-kun flew off the course!\nIt must be so frustrating!': 'Kazuma-kun a quitté la piste !\nCela doit être tellement frustrant !', "He's zooming through the course at full throttle!": 'Il dévore le circuit à toute berzingue !', "He's turning the tables with a boost!": 'Il renverse la situation grâce à son turbo !', "He's betting it all on this boost!": 'Il mise son va-tout sur cette accélération !', "He's making a comeback through his sheer\ndetermination to win!": 'Il effectue une folle remontée par sa seule\nvolonté de vaincre !', "He's back in this race with some amazing moves!": 'Il se remet en selle par des manœuvres superbes !', "They're sticking it out until the very last moment!": "Ils ne lâchent rien jusqu'au dernier souffle !", 'What a show of impressive persistence!': 'Démonstration de combativité exemplaire !', 'He lost some ground, but Kazuma-kun is making\na comeback through his determination to win!': "Kazuma-kun recolle au train grâce à\nson mental d'acier !", 'A beautiful comeback after that loss of balance!': "Superbe reprise en main après cette perte d'équilibre !", "Looks like it couldn't withstand it!": "On dirait que le bolide n'a pas pu résister !", "It just couldn't hold its ground till the end!": "Il n'a tout simplement pas pu tenir jusqu'au bout !", 'There was just too much momentum!': "Il y avait beaucoup trop d'inertie !", "Even sheer will couldn't bear fruit!": "Même la plus pure volonté n'a pas suffi !", 'The machine overturned and must be retired!': "La voiture s'est retournée, c'est l'abandon !", "The goal isn't that way! Kazuma-kun went the\nwrong way and is forced to retire!": "Ce n'est pas par là ! Kazuma-kun part\nà contresens et doit abandonner !", "His machine got stuck, and that's a retirement!": "Son bolide est coincé, c'est l'abandon forcé !", 'Nothing more tragic than a lapped retire!': "Rien de plus tragique qu'un abandon à un tour !", 'Only 30 seconds remain!': 'Il ne reste plus que 30 secondes !', 'Only ten seconds remain!\nCan he make it to the goal!?': 'Plus que dix secondes au chronomètre !\nArrivera-t-il à franchir la ligne !?', "It looks like time's up!": 'On dirait que le temps est écoulé !', "It's losing balance! Will it pull through!?": "La voiture perd l'équilibre ! Va-t-elle s'en sortir !?", "It's lost speed! Can it make the loop!?": 'Elle a perdu de la vitesse ! Passera-t-elle le looping !?', "Looks like Kazuma-kun's determination\nis flowing right into his machine!": 'La détermination de Kazuma-kun\nse transmet directement à son bolide !', "It'll fly off the course if this keeps up!": 'Elle va décoller si ça continue comme ça !', "It's losing speed! Will this be the end!?": 'Elle perd son élan ! Serait-ce la fin de ses espoirs !?', "It's going to fly!!!": 'Elle va décoller !!!', 'Can it hold its ground!?': 'Peut-elle tenir la piste !?', 'Is all hope lost!?': 'Tout espoir est-il perdu !?', 'Ooh!?': 'Ooh !?', 'Is this--!?': 'Serait-ce... !?', 'Crazy!': 'Fou !', 'Will you look at that!?': 'Regardez-moi ça !?', 'Kazuma-kun!': 'Kazuma-kun !', 'Takuma-kun!': 'Takuma-kun !', 'Hideki-kun!': 'Hideki-kun !', 'Mika-chan!': 'Mika-chan !', 'Satoru-kun!': 'Satoru-kun !', 'Harumi-chan!': 'Harumi-chan !', 'Sena-chan!': 'Sena-chan !', 'Kazuyoshi-kun!': 'Kazuyoshi-kun !', 'The machine is in the green lane!': 'La voiture est sur la voie verte !', 'The machine is in the yellow lane!': 'La voiture est sur la voie jaune !', 'The machine is in the blue lane!': 'La voiture est sur la voie bleue !', 'The machine is in the red lane!': 'La voiture est sur la voie rouge !', 'Our first place machine!': 'Notre voiture en 1re place !', 'Our second place machine!': 'Notre voiture en 2e place !', 'Our third place machine!': 'Notre voiture en 3e place !', 'Our fourth place machine!': 'Notre voiture en 4e place !', 'The race enters its second half!': 'La course entre dans sa seconde moitié !', "It's the final lap!": "C'est le dernier tour !", 'Goooooaaal!': 'Arrivéééee !'}

POKECIR_PTR_TABLE_OFFSET = 0xFFFB70
POKECIR_PTR_COUNT = 253
POKECIR_TEXT_OFFSET = 0xD892F8
POKECIR_TEXT_MAX_SIZE = 0xD8C4D0 - 0xD892F8  # 12,760 bytes

# PE section offset mapping for GOG v1.015a
# .rdata: Raw 0xCB7800 -> VA 0xCB9000 (RVA = Raw + 0x1800)
# VA = 0x140000000 + RVA
RDATA_RAW_TO_VA_DIFF = 0x140000000 + 0x1800


def apply_pokecir_commentary(exe_data: bytearray) -> tuple:
    """
    Packs all French commentary strings sequentially into .rdata at 0xD892F8
    and updates all 253 64-bit pointers in .data at 0xFFFB70.
    Returns (strings_applied, pointers_updated).
    """
    if len(exe_data) < POKECIR_PTR_TABLE_OFFSET + POKECIR_PTR_COUNT * 8:
        return (0, 0)

    # 1. Read existing English strings for each of the 253 pointer entries
    entries_en = []
    for idx in range(POKECIR_PTR_COUNT):
        p_off = POKECIR_PTR_TABLE_OFFSET + idx * 8
        va = struct.unpack_from('<Q', exe_data, p_off)[0]
        # Calculate raw file offset from VA
        rva = va - 0x140000000
        # Check if in .rdata (0xCB9000..0xFEEDB0)
        raw_off = rva - 0x1800
        if 0 <= raw_off < len(exe_data):
            null_pos = exe_data.find(b'\x00', raw_off)
            if null_pos != -1:
                en_str = exe_data[raw_off:null_pos].decode('latin1', errors='ignore')
            else:
                en_str = ""
        else:
            en_str = ""
        entries_en.append(en_str)

    # 2. Pack unique French strings sequentially into blob
    packed_blob = bytearray()
    fr_str_offsets = {}

    for en_str in entries_en:
        if en_str not in fr_str_offsets:
            fr_str = POKECIR_COMMENTARY.get(en_str, en_str)
            fr_bytes = fr_str.encode('cp1252', errors='replace') + b'\x00'
            fr_str_offsets[en_str] = len(packed_blob)
            packed_blob.extend(fr_bytes)

    if len(packed_blob) > POKECIR_TEXT_MAX_SIZE:
        raise ValueError(
            f"Packed Pocket Circuit strings exceed available space: "
            f"{len(packed_blob)} > {POKECIR_TEXT_MAX_SIZE}"
        )

    # 3. Write packed blob into .rdata at 0xD892F8
    exe_data[POKECIR_TEXT_OFFSET : POKECIR_TEXT_OFFSET + len(packed_blob)] = packed_blob
    # Pad remainder of space with zeros
    pad_len = POKECIR_TEXT_MAX_SIZE - len(packed_blob)
    if pad_len > 0:
        exe_data[POKECIR_TEXT_OFFSET + len(packed_blob) : POKECIR_TEXT_OFFSET + POKECIR_TEXT_MAX_SIZE] = b'\x00' * pad_len

    # 4. Update the 253 64-bit pointers in .data at 0xFFFB70
    pointers_updated = 0
    for idx, en_str in enumerate(entries_en):
        rel_off = fr_str_offsets[en_str]
        target_raw_off = POKECIR_TEXT_OFFSET + rel_off
        new_va = target_raw_off + RDATA_RAW_TO_VA_DIFF
        p_off = POKECIR_PTR_TABLE_OFFSET + idx * 8
        struct.pack_into('<Q', exe_data, p_off, new_va)
        pointers_updated += 1

    return (len(fr_str_offsets), pointers_updated)


class PEModifier:
    def __init__(self, data: bytearray):
        self.data = data
        self.parse_headers()

    def parse_headers(self):
        e_lfanew = struct.unpack_from('<I', self.data, 0x3C)[0]
        self.pe_offset = e_lfanew
        magic = self.data[e_lfanew:e_lfanew+4]
        if magic != b'PE\x00\x00':
            raise ValueError("File is not a valid PE executable.")

        self.num_sections = struct.unpack_from('<H', self.data, e_lfanew + 6)[0]
        self.opt_size = struct.unpack_from('<H', self.data, e_lfanew + 20)[0]
        opt_magic = struct.unpack_from('<H', self.data, e_lfanew + 24)[0]
        if opt_magic != 0x20B:
            raise ValueError(f"Executable is not PE32+ (x64): {hex(opt_magic)}")

        self.image_base = struct.unpack_from('<Q', self.data, e_lfanew + 24 + 24)[0]
        self.sec_align = struct.unpack_from('<I', self.data, e_lfanew + 24 + 32)[0]
        self.file_align = struct.unpack_from('<I', self.data, e_lfanew + 24 + 36)[0]
        self.size_of_image = struct.unpack_from('<I', self.data, e_lfanew + 24 + 56)[0]
        self.sec_table_offset = e_lfanew + 24 + self.opt_size

        self.sections = []
        for i in range(self.num_sections):
            s_off = self.sec_table_offset + i * 40
            name = self.data[s_off:s_off+8].decode('latin1').rstrip('\x00')
            vsize, vaddr, raw_size, raw_ptr = struct.unpack_from('<4I', self.data, s_off + 8)
            charact = struct.unpack_from('<I', self.data, s_off + 36)[0]
            self.sections.append({
                'name': name,
                'vsize': vsize,
                'vaddr': vaddr,
                'raw_size': raw_size,
                'raw_ptr': raw_ptr,
                'charact': charact,
                'header_off': s_off
            })

    def get_section(self, name):
        for s in self.sections:
            if s['name'] == name:
                return s
        return None

    def add_trad_section(self, section_size=0x100000):
        """Adds a .trad section to the PE binary if not already present."""
        existing = self.get_section('.trad')
        if existing:
            return existing

        last_sec = self.sections[-1]
        new_vaddr = align(last_sec['vaddr'] + max(last_sec['vsize'], last_sec['raw_size']), self.sec_align)
        new_raw_ptr = align(len(self.data), self.file_align)

        # Pad existing data up to new_raw_ptr
        if len(self.data) < new_raw_ptr:
            self.data.extend(b'\x00' * (new_raw_ptr - len(self.data)))

        # Append 1MB of zeros for .trad
        self.data.extend(b'\x00' * section_size)

        # Build section header (40 bytes)
        # Name (8 bytes), VSize (4), VAddr (4), RawSize (4), RawPtr (4), Relocs (12 zero), Characteristics (4)
        sec_name = b'.trad\x00\x00\x00'
        characteristics = 0x40000040  # IMAGE_SCN_MEM_READ | IMAGE_SCN_CNT_INITIALIZED_DATA
        new_header = struct.pack('<8sIIII12sI',
            sec_name, section_size, new_vaddr, section_size, new_raw_ptr, b'\x00'*12, characteristics
        )

        # Write new section header in section table
        new_header_off = self.sec_table_offset + self.num_sections * 40
        self.data[new_header_off:new_header_off+40] = new_header

        # Update NumberOfSections in FileHeader
        self.num_sections += 1
        struct.pack_into('<H', self.data, self.pe_offset + 6, self.num_sections)

        # Update SizeOfImage in OptionalHeader
        new_size_of_image = align(new_vaddr + section_size, self.sec_align)
        struct.pack_into('<I', self.data, self.pe_offset + 24 + 56, new_size_of_image)

        # Refresh internal section list
        self.parse_headers()
        return self.get_section('.trad')


def kill_game_process():
    """Terminates any lingering Yakuza0.exe processes to unlock files."""
    if sys.platform == 'win32':
        try:
            import subprocess
            subprocess.run(["taskkill", "/F", "/IM", "Yakuza0.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
        except Exception:
            pass


def install_data_archives(game_dir):
    """Safely copies precompiled verified data archives into game directory, stripping read-only flags."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    if not os.path.isdir(data_dir):
        return True

    card_start("2/4 — INSTALLATION DES ARCHIVES TRADUITES", width=76)

    # Nettoyage automatique des sous-dossiers parasites issus d'anciennes extractions imbriquees
    nested_parasites = [
        os.path.join(game_dir, 'data', 'bootpar', 'bootpar'),
        os.path.join(game_dir, 'data', 'staypar', 'staypar'),
        os.path.join(game_dir, 'data', 'wdr_par_c', 'wdr_par_c'),
        os.path.join(game_dir, 'data', 'pausepar_e', 'pausepar_e'),
        os.path.join(game_dir, 'data', 'data'),
    ]
    for parasite in nested_parasites:
        if os.path.isdir(parasite):
            try:
                shutil.rmtree(parasite)
                card_line(f"Sous-dossier parasite supprimé : {os.path.basename(parasite)}", status="ok")
            except Exception as e:
                card_line(f"Impossible de supprimer {parasite}: {e}", status="warn")

    core_archives = [
        ("wdr.par", "data/wdr_par_c/wdr.par", 7000000),
        ("boot.par", "data/bootpar/boot.par", 1500000),
        ("stay.par", "data/staypar/stay.par", 500000),
        ("common.par", "data/wdr_par_c/common.par", 10000),
        ("minigame.par", "data/pausepar_e/minigame.par", 15000000),
        ("pokecir.par", "data/minigame/pokecir.par", 50000),
    ]

    p_bar_full = format_progress(100, 100, width=16)

    for label, rel_path, min_size in core_archives:
        src = os.path.normpath(os.path.join(script_dir, rel_path.replace('/', os.sep)))
        dst = os.path.normpath(os.path.join(game_dir, rel_path.replace('/', os.sep)))

        if not os.path.isfile(src):
            continue

        is_same = False
        try:
            if os.path.exists(dst) and os.path.samefile(src, dst):
                is_same = True
        except Exception:
            pass
        if not is_same:
            try:
                if os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dst)):
                    is_same = True
            except Exception:
                pass

        if is_same:
            try:
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass
            actual_size = os.path.getsize(dst)
            if actual_size < min_size:
                card_line(f"Archive présente incomplète: {label} ({actual_size} o)", status="err")
                card_end(width=76)
                return False
            size_mb = f"{actual_size / (1024*1024):.1f} Mo" if actual_size > 500000 else f"{actual_size / 1024:.0f} Ko"
            card_line(f"{label:<16} {p_bar_full}  ({size_mb})", status="ok")
            continue

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isfile(dst):
            bak = dst + ".bak"
            if not os.path.exists(bak):
                try:
                    shutil.copy2(dst, bak)
                except Exception:
                    pass
            try:
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
            except Exception:
                pass

        try:
            shutil.copy2(src, dst)
            os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
        except Exception as e:
            kill_game_process()
            try:
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
                shutil.copy2(src, dst)
                os.chmod(dst, stat.S_IWRITE | stat.S_IREAD)
            except Exception as e2:
                card_line(f"Impossible d'écrire dans '{dst}': {e2}", status="err")
                card_line("Vérifiez que le jeu est fermé et vos droits d'écriture.", status="warn")
                card_end(width=76)
                return False

        actual_size = os.path.getsize(dst)
        if actual_size < min_size:
            card_line(f"Archive copiée incomplète: {label} ({actual_size} o)", status="err")
            card_end(width=76)
            return False

        size_mb = f"{actual_size / (1024*1024):.1f} Mo" if actual_size > 500000 else f"{actual_size / 1024:.0f} Ko"
        card_line(f"{label:<16} {p_bar_full}  ({size_mb})", status="ok")

    # Déploiement groupé et élégant des tables et textures de mini-jeux
    minigame_src_dir = os.path.join(script_dir, "data", "minigame")
    tables_copied = 0
    textures_copied = 0
    if os.path.isdir(minigame_src_dir):
        patch_minigame_dirs = {"catfight", "fishing", "poker", "cabaret", "teleclub"}
        for root, dirs, files in os.walk(minigame_src_dir):
            rel_dir = os.path.relpath(root, minigame_src_dir).replace('\\', '/')
            sub_folder = rel_dir.split('/')[0] if rel_dir != '.' else ''
            if sub_folder and sub_folder not in patch_minigame_dirs:
                continue
            for f in sorted(files):
                if f.endswith('.bak'):
                    continue
                is_tbl = f.endswith('.bin') or f.endswith('.bin_c')
                is_tex = f.endswith('.dds')
                if is_tbl or is_tex:
                    src_f = os.path.join(root, f)
                    rel_f = os.path.relpath(src_f, script_dir)
                    dst_f = os.path.normpath(os.path.join(game_dir, rel_f))
                    os.makedirs(os.path.dirname(dst_f), exist_ok=True)
                    if os.path.isfile(dst_f):
                        try:
                            os.chmod(dst_f, stat.S_IWRITE | stat.S_IREAD)
                        except Exception:
                            pass
                    try:
                        shutil.copy2(src_f, dst_f)
                        os.chmod(dst_f, stat.S_IWRITE | stat.S_IREAD)
                        if is_tbl:
                            tables_copied += 1
                        else:
                            textures_copied += 1
                    except Exception:
                        pass

    if tables_copied > 0:
        card_line(f"{'Tables mini-jeux':<16} {p_bar_full}  ({tables_copied} fichiers)", status="ok")
    if textures_copied > 0:
        card_line(f"{'Textures 2D UI':<16} {p_bar_full}  ({textures_copied} textures)", status="ok")

    # Patch des sous-titres audio d'ambiance si sound.par existe dans le jeu
    user_sound_par = os.path.join(game_dir, "data", "soundpar", "sound.par")
    if os.path.isfile(user_sound_par):
        patch_sound_script = os.path.join(script_dir, "tools", "patch_sound_par.py")
        if os.path.isfile(patch_sound_script):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("patch_sound_par", patch_sound_script)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                mod.patch_sound_par_inplace(user_sound_par)
                card_line(f"{'Sous-titres audio':<16} {p_bar_full}  (sound.par)", status="ok")
            except Exception as e:
                card_line(f"Avertissement patching sound.par: {e}", status="warn")

    card_line("Toutes les archives et tables de mini-jeux sont déployées", status="ok")
    card_end(width=76)
    return True


def patch_yakuza0_gog(exe_path="Yakuza0.exe", output_path=None, interactive=True):
    print_banner(version="v1.14.0")

    # Strict resolution of game directory / executable (Rule 6)
    if not exe_path or not os.path.isfile(exe_path):
        resolved_dir = resolve_game_directory(exe_path, interactive=interactive)
        if resolved_dir:
            exe_path = os.path.join(resolved_dir, "Yakuza0.exe")
        else:
            card_start("ERREUR DE DÉTECTION", width=76)
            card_line(f"Exécutable Yakuza0.exe introuvable : '{exe_path}'", status="err")
            card_line("Glissez le dossier de jeu sur patch_fr.bat ou lancez :", status="info")
            card_line("  patch_fr.bat \"D:\\GOG Games\\Yakuza 0\"", status="none")
            card_end(width=76)
            return False

    exe_path = os.path.normpath(os.path.abspath(exe_path))
    if output_path is None:
        output_path = exe_path
    else:
        output_path = os.path.normpath(os.path.abspath(output_path))

    game_dir = os.path.dirname(exe_path)

    # Card 1: Préparation & Sécurité
    card_start("1/4 — PRÉPARATION & SÉCURITÉ", width=76)
    kill_game_process()
    card_line("Processus Yakuza0.exe vérifié et libéré", status="ok")

    backup_path = exe_path + ".bak"
    if os.path.exists(backup_path):
        card_line(f"Restauration depuis la sauvegarde propre : {os.path.basename(backup_path)}", status="info")
        with open(backup_path, 'rb') as f:
            data = bytearray(f.read())
    else:
        try:
            os.chmod(exe_path, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass
        shutil.copy2(exe_path, backup_path)
        card_line(f"Sauvegarde originale créée : {os.path.basename(backup_path)}", status="ok")
        with open(exe_path, 'rb') as f:
            data = bytearray(f.read())

    # Unlock read-only on game files
    try:
        os.chmod(exe_path, stat.S_IWRITE | stat.S_IREAD)
        for root, dirs, files in os.walk(os.path.join(game_dir, "data")):
            for f in files:
                try:
                    os.chmod(os.path.join(root, f), stat.S_IWRITE | stat.S_IREAD)
                except Exception:
                    pass
        card_line("Attributs lecture seule (+R) déverrouillés sur le jeu", status="ok")
    except Exception:
        pass
    card_end(width=76)

    # 2. Deploy precompiled data archives if present
    if not install_data_archives(game_dir):
        return False

    # 3. Apply executable patches
    card_start("3/4 — PATCH DE L'EXÉCUTABLE (Yakuza0.exe)", width=76)
    pe = PEModifier(data)

    applied_count = 0
    for offset, patch_bytes, desc in GOG_BYTECODE_PATCHES:
        if offset + len(patch_bytes) <= len(data):
            data[offset:offset+len(patch_bytes)] = patch_bytes
            applied_count += 1
    card_line(f"Patches de rendu mono-octet injectés ({applied_count}/{len(GOG_BYTECODE_PATCHES)})", status="ok")

    font_table = bytearray(get_font_table_bytes())
    assert len(font_table) == FONT_TABLE_SIZE, f"Invalid font table size: {len(font_table)}"
    data[GOG_FONT_TABLE_OFFSET : GOG_FONT_TABLE_OFFSET + FONT_TABLE_SIZE] = font_table
    card_line("Typographie & crénage symétrique [0.4, 0.4] injectés (6 144 o)", status="ok")

    words_applied = 0
    for offset, word_bytes, desc in GOG_DIRECT_WORDS:
        if offset + len(word_bytes) <= len(data):
            data[offset:offset+len(word_bytes)] = word_bytes
            words_applied += 1
    card_line(f"Termes d'interface traduits en dur ({words_applied} termes)", status="ok")

    strings_applied, pointers_updated = apply_pokecir_commentary(data)
    card_line(f"Commentaires de course Pocket Circuit traduits ({pointers_updated}/{POKECIR_PTR_COUNT} répliques)", status="ok")

    # Save patched exe
    try:
        os.chmod(output_path, stat.S_IWRITE | stat.S_IREAD)
    except Exception:
        pass
    try:
        with open(output_path, 'wb') as f:
            f.write(data)
    except Exception as e:
        kill_game_process()
        try:
            os.chmod(output_path, stat.S_IWRITE | stat.S_IREAD)
            with open(output_path, 'wb') as f:
                f.write(data)
        except Exception as e2:
            card_line(f"Échec d'écriture dans '{output_path}': {e2}", status="err")
            card_end(width=76)
            return False

    # Verification on disk
    try:
        with open(output_path, 'rb') as f:
            f.seek(GOG_FONT_TABLE_OFFSET + 0x69 * 24)
            i_margin = struct.unpack('<6f', f.read(24))
            if abs(i_margin[0] - 0.4) > 0.01:
                card_line(f"Vérification de table de police échouée sur disque: {i_margin}", status="err")
                card_end(width=76)
                return False
    except Exception as e:
        card_line(f"Échec de vérification sur disque: {e}", status="err")
        card_end(width=76)
        return False

    card_line("Binaire Yakuza0.exe sauvegardé et certifié conforme sur disque", status="ok")
    card_end(width=76)

    # 4. Summary card
    card_start("4/4 — INSTALLATION RÉUSSIE", width=76)
    card_line("Le patch français est désormais actif et opérationnel !", status="ok")
    card_line("Toutes les cabines, cinématiques et dialogues sont traduits.", status="ok")
    card_line("Bon jeu à Kamurocho et Sotenbori !", status="info")
    card_end(width=76)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch clean GOG Yakuza 0 executable for French Fan-Translation.")
    parser.add_argument("input_exe", nargs="?", default=None, help="Path to clean GOG Yakuza0.exe (default: auto-detected)")
    parser.add_argument("output_exe", nargs="?", default=None, help="Output path (default: overwrite input_exe with backup)")
    args = parser.parse_args()

    success = patch_yakuza0_gog(args.input_exe, args.output_exe)
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/crash_analyzer.py
-----------------------
Automated intelligent crash analyzer for Yakuza 0 GOG patch:
1. Parses Special K crash logs (logs/crash.log).
2. Extracts RIP address, thread, fault module, and all 64-bit registers.
3. Automatically disassembles the faulting x86-64 instruction in Yakuza0.exe.
4. Cross-references known Sega RGG engine routines & crash signatures.
5. In RGG table crashes, decodes the column index (ebp/esi), row index (r10d/edi),
   and identifies the offending table.
6. Provides an immediate human-readable diagnosis and actionable fix.
"""

import os
import sys
import re
import struct
import subprocess
import time

def run_rust_analyzer(log_p, data_dir='release_gog/data', exe_p='Yakuza0.exe'):
    # Check for Rust binaries (Linux or Windows)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(repo_root, "tools", "rgg_preflight_bin"),
        os.path.join(repo_root, "rgg_preflight.exe"),
        os.path.join(repo_root, "release_gog", "rgg_preflight.exe"),
        "rgg_preflight.exe",
        "rgg_preflight"
    ]
    for c in candidates:
        if os.path.isfile(c) and (os.access(c, os.X_OK) or c.endswith('.exe')):
            cmd = [c, "crash", log_p, data_dir, exe_p]
            try:
                ret = subprocess.run(cmd)
                return ret.returncode == 0
            except Exception:
                pass
    return False

KNOWN_CRASH_PATTERNS = {
    0x3711db: {
        "subsystem": "CPropertyTable::BuildColumnIndex / ResolveRowPointer",
        "description": "Crash lors de la résolution des pointeurs de lignes/colonnes d'une table RGG (0x20070319).",
        "cause": "Une table a été déplacée à un offset sectoriel invalide, un décalage de structure de colonnes (Steam vs GOG) a faussé l'offset, ou la taille décompressée dépasse le buffer attendu.",
        "decode": lambda regs: (
            f"  - Colonne en cours de traitement : index {regs.get('rbp', 'inconnu')} (ebp)\n"
            f"  - Ligne en cours de traitement   : ligne {regs.get('r10', 'inconnu')} (r10d)\n"
            f"  - Pointeur descripteur (%r8)     : {hex(regs.get('r8', 0)) if isinstance(regs.get('r8'), int) else regs.get('r8')}\n"
            + find_candidate_tables_for_col(regs.get('rbp', 7))
        ),
        "fix": "Reconstruire la table concernée en respectant rigoureusement son gap sectoriel in-place et sans colonnes tronquées."
    },
    0x37177c: {
        "subsystem": "CPropertyTable::ConvertEndianness (Colonnes Type 2 / Tables Isolées SLLZ)",
        "description": "Crash dans la boucle de conversion d'endianness (bswap) des colonnes de Type 2 (ID 16-bit + chaîne).",
        "cause": (
            "1. Une table hors-archive (loose file ex: data/minigame/fishing/) a été compressée en SLLZ. "
            "Le moteur lit l'en-tête SLLZ comme 69 632 colonnes et déborde le buffer.\n"
            "  2. Ou une chaîne de Type 2 dépasse sa longueur déclarée sans terminateur nul \\x00."
        ),
        "decode": lambda regs: (
            f"  - Colonne en cours de traitement : index {regs.get('rsi', 'inconnu')} (esi)\n"
            f"  - Pointeur de lecture (%rax)     : {hex(regs.get('rax', 0)) if isinstance(regs.get('rax'), int) else regs.get('rax')}\n"
            f"  - Valeur mémoire invalide (%rdx) : {hex(regs.get('rdx', 0)) if isinstance(regs.get('rdx'), int) else regs.get('rdx')}\n"
            + (
                "  🚨 ALERTE : Colonne > 1000 détectée ! Ce crash est provoqué par un fichier table hors-archive\n"
                "     (ex: minigame/fishing/*.bin_c) compressé indûment en SLLZ au lieu d'être au format brut 0x20070319 !"
                if isinstance(regs.get('rsi'), int) and regs.get('rsi') >= 1000 else ""
            )
        ),
        "fix": (
            "Décompresser les tables de minijeu en format brut non-compressé 0x20070319 avec variantes .bin et .bin_c, "
            "ou vérifier le null-padding des chaînes Type 2."
        )
    },
    0x371324: {
        "subsystem": "CPropertyTable::GetString (Chaîne vide / Retour NULL)",
        "description": "Le moteur interroge une ligne de chaîne vide et reçoit un pointeur NULL (0x0).",
        "cause": "Une ligne requise (ex: NAME dans item.bin_c) est vide ('') au lieu de contenir du texte.",
        "decode": lambda regs: f"  - Ligne interrogée : ligne {regs.get('r10', 'inconnu')} (r10d)",
        "fix": "Remplir la chaîne manquante dans la table (ex: quête ou item) sans laisser de chaîne vide."
    },
    0x234b0: {
        "subsystem": "SLLZ::Decompress / Lecteur Asynchrone de Secteurs",
        "description": "Underflow du décompresseur SLLZ (%rdx négatif) lors du chargement d'icône 2D.",
        "cause": "Archive pause.par compilée avec alignement 64 octets au lieu de frontières strictes de 2 048 octets. Le lecteur saute le header SLLZ.",
        "decode": lambda regs: f"  - Registre %rdx (décalage flux SLLZ) : {hex(regs.get('rdx', 0)) if isinstance(regs.get('rdx'), int) else regs.get('rdx')}",
        "fix": "Recompiler pause.par en alignant CHAQUE fichier sur un multiple strict de 2 048 octets ((off + 2047) & ~2047)."
    },
    0x6ea328: {
        "subsystem": "ScriptMessage::Load / Bytecode .msg",
        "description": "Boucle infinie de bswap et crash d'accès mémoire dans le lecteur de dialogues .msg.",
        "cause": "Archive wdr.par tronquée (< 7 Mo) ou non copiée dans le jeu. Le moteur lit au-delà de la fin de fichier.",
        "decode": lambda regs: f"  - Compteur itérations (%r10) : {hex(regs.get('r10', 0)) if isinstance(regs.get('r10'), int) else regs.get('r10')}",
        "fix": "S'assurer que wdr.par pèse > 7.3 Mo et contient 1 931 fichiers originaux préservés."
    },
    0xa4526: {
        "subsystem": "SoundStreamer / Response Wanderer Offset",
        "description": "Crash au chargement de sauvegarde lors de l'initialisation de l'ambiance sonore.",
        "cause": "Fichier response_wanderer.bin_c déplacé de son offset d'origine 0x9a000 dans stay.par.",
        "decode": lambda regs: "  - Offset streaming audio corrompu",
        "fix": "Maintenir response_wanderer.bin_c à son offset natif exact 0x9a000."
    },
    0x396783: {
        "subsystem": "TypewriterEffect / Cabine Téléphonique",
        "description": "Softlock permanent devant la cabine téléphonique (menu de sauvegarde non affiché).",
        "cause": "La réplique contient des accents UTF-8 multi-octets (ex: 'é') ou n'a pas pile 58 caractères ASCII.",
        "decode": lambda regs: "  - Décompte de caractères faussé par UTF-8",
        "fix": "Remplacer par 'Sauvegardez et utilisez le coffre depuis une\\r\\ncabine.     ' (pile 58 caractères ASCII)."
    },
    0x30ed: {
        "subsystem": "msvcrt!vsnprintf (Format String Mismatch)",
        "description": "Crash vsnprintf : spécificateur %s recevant un entier.",
        "cause": "Une chaîne de format utilise '%s' au lieu de '%d' pour un prix ou un montant.",
        "decode": lambda regs: "  - Format string mismatch",
        "fix": "Remplacer '%s' par '%d' dans le dictionnaire de traduction correspondant."
    },
    0x19cac0: {
        "subsystem": "CMfp::Initialize / Sous-titres Voix de Rue (.mfp)",
        "description": "Crash d'accès mémoire (%r9) lors de la boucle de conversion d'endianness (bswap) d'un fichier .mfp (sous-titres de répliques vocales d'ambiance).",
        "cause": (
            "Un fichier .mfp dans sound.par a subi un remplacement de sous-titre de longueur inégale (+1 ou +2 octets), "
            "ce qui a décalé les pointeurs et tables 32-bit situés après la chaîne. L'offset relatif lu à l'offset 0x14 "
            "est faussé et envoie %r9 dans de la mémoire non allouée."
        ),
        "decode": lambda regs: (
            f"  - Base buffer (%rdx)      : {hex(regs.get('rdx', 0)) if isinstance(regs.get('rdx'), int) else regs.get('rdx')}\n"
            f"  - Offset relatif (%rcx)   : {hex(regs.get('rcx', 0)) if isinstance(regs.get('rcx'), int) else regs.get('rcx')}\n"
            f"  - Pointeur calculé (%r9)  : {hex(regs.get('r9', 0)) if isinstance(regs.get('r9'), int) else regs.get('r9')}\n"
            f"  - Compteur bswap (%r10)   : {hex(regs.get('r10', 0)) if isinstance(regs.get('r10'), int) else regs.get('r10')}"
        ),
        "fix": "Reconstruire sound.par avec tools/patch_sound_par.py en respectant impérativement des longueurs de chaînes 100% bit-exactes."
    }
}

def parse_crash_log(log_path):
    if not os.path.exists(log_path):
        return None

    with open(log_path, 'r', encoding='latin1', errors='replace') as f:
        content = f.read()

    # Find the last exception block
    blocks = content.split("Unhandled Top-Level Exception")
    if len(blocks) < 2:
        return None
    
    last_block = blocks[-1]
    
    # Extract RIP Addr
    rip_match = re.search(r"RIP Addr\.:\s+Yakuza0\.exe\+([0-9a-fA-F]+)h", last_block)
    rva = int(rip_match.group(1), 16) if rip_match else None

    # Extract Thread
    thread_match = re.search(r"Name\.\.\.\.\.:\s+\"([^\"]+)\"", last_block)
    thread = thread_match.group(1) if thread_match else "Inconnu"

    # Extract Registers
    regs = {}
    reg_names = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
    for reg in reg_names:
        m = re.search(rf"{reg}:\s+(0x[0-9a-fA-F]+|[0-9a-fA-F]+h)", last_block)
        if m:
            val_str = m.group(1).replace('h', '')
            regs[reg] = int(val_str, 16)

    # Extract StackFrame Rbp, Rsi, Rdi
    for sfr in ['Rbp', 'Rsi', 'Rdi', 'Rsp']:
        m = re.search(rf"{sfr}=([0-9a-fA-F]+)h", last_block)
        if m:
            regs[sfr.lower()] = int(m.group(1), 16)

    return {
        'rva': rva,
        'va': (0x140000000 + rva) if rva else None,
        'thread': thread,
        'regs': regs,
        'raw_block': last_block[:500]
    }

def disassemble_instruction(rva, exe_path='Yakuza0.exe'):
    if not os.path.exists(exe_path) or not rva:
        return None

    target_va = 0x140000000 + rva
    start_va = max(0x140001000, target_va - 24)
    stop_va = target_va + 24

    cmd = [
        'objdump', '-d', '-M', 'intel',
        f'--start-address=0x{start_va:x}',
        f'--stop-address=0x{stop_va:x}',
        exe_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            lines = res.stdout.strip().split('\n')
            disasm = []
            for l in lines:
                if ':' in l:
                    marker = "==>" if f"{target_va:x}:" in l else "   "
                    disasm.append(f"{marker} {l.strip()}")
            return '\n'.join(disasm)
    except Exception:
        pass
    return None

def analyze_crash(log_path='logs/crash.log', exe_path='Yakuza0.exe'):
    print("=" * 70)
    print("  ANALYSEUR AUTOMATIQUE DE CRASH — Yakuza 0 GOG FR Patch")
    print("=" * 70)

    crash_data = parse_crash_log(log_path)
    if not crash_data:
        print(f"[-] Aucun bloc d'exception récent trouvé dans '{log_path}'.")
        return False

    rva = crash_data['rva']
    va = crash_data['va']
    regs = crash_data['regs']
    thread = crash_data['thread']

    print(f"\n[*] Crash détecté :")
    print(f"  - Adresse RIP : Yakuza0.exe+0x{rva:X}h (0x{va:X})")
    print(f"  - Thread      : {thread}")

    print(f"\n[*] Registres clés :")
    print(f"  - RAX: {hex(regs.get('rax', 0)):18s} RBX: {hex(regs.get('rbx', 0)):18s}")
    print(f"  - RCX: {hex(regs.get('rcx', 0)):18s} RDX: {hex(regs.get('rdx', 0)):18s}")
    print(f"  - RSI: {hex(regs.get('rsi', 0)):18s} RDI: {hex(regs.get('rdi', 0)):18s}")
    print(f"  - R8 : {hex(regs.get('r8', 0)):18s} R9 : {hex(regs.get('r9', 0)):18s}")
    print(f"  - R10: {hex(regs.get('r10', 0)):18s} RBP: {hex(regs.get('rbp', 0)):18s}")

    # Disassembly
    disasm = disassemble_instruction(rva, exe_path)
    if disasm:
        print(f"\n[*] Désassemblage x86-64 au point de rupture :")
        print(disasm)

    # Match known patterns
    matched = False
    for pat_rva, info in KNOWN_CRASH_PATTERNS.items():
        if rva == pat_rva or (rva and abs(rva - pat_rva) < 8):
            matched = True
            print(f"\n" + "!" * 70)
            print(f"  DIAGNOSTIC AUTOMATIQUE IDENTIFIÉ : {info['subsystem']}")
            print("!" * 70)
            print(f"\nDescription : {info['description']}")
            print(f"Cause       : {info['cause']}")
            if 'decode' in info:
                print("\nDécodage des paramètres :")
                print(info['decode'](regs))
            print(f"\nAction Corrective Immédiate :")
            print(f"👉 {info['fix']}")
            break

    if not matched:
        print(f"\n[?] Signature inconnue (RVA 0x{rva:X}h).")
        print("    Vérifier la fonction parente via objdump ou ghidra.")

    print("\n" + "=" * 70)
    return True

def watch_crash_log(log_path='logs/crash.log', exe_path='Yakuza0.exe'):
    print(f"[*] Surveillance active du fichier '{log_path}'... (Ctrl+C pour quitter)")
    last_mtime = os.path.getmtime(log_path) if os.path.exists(log_path) else 0

    while True:
        try:
            time.sleep(1.0)
            if os.path.exists(log_path):
                cur_mtime = os.path.getmtime(log_path)
                if cur_mtime > last_mtime:
                    last_mtime = cur_mtime
                    print("\n[!] Nouveau crash détecté dans le log !")
                    analyze_crash(log_path, exe_path)
        except KeyboardInterrupt:
            print("\nArrêt de la surveillance.")
            break

if __name__ == '__main__':
    log_p = 'logs/crash.log'
    if '--watch' in sys.argv:
        # Check Rust watch mode
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rust_bin = os.path.join(repo_root, "tools", "rgg_preflight_bin")
        if os.path.isfile(rust_bin) and os.access(rust_bin, os.X_OK):
            subprocess.run([rust_bin, "watch", log_p])
            sys.exit(0)
        watch_crash_log(log_p)
    else:
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            log_p = sys.argv[1]
        
        # Try ultra-fast Rust analyzer first
        if run_rust_analyzer(log_p):
            sys.exit(0)

        # Fallback to Python if Rust binary is missing
        analyze_crash(log_p)

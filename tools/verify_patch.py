#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_patch.py — Vérificateur d'intégrité du patch FR Yakuza 0 GOG
====================================================================
Script AUTONOME à exécuter sur le PC de jeu après application du patch.
Ne nécessite AUCUN fichier original GOG pour la vérification.

Usage:
  python3 verify_patch.py                          (cherche release_gog/ dans le répertoire courant)
  python3 verify_patch.py /chemin/vers/Yakuza0/    (pointe vers le dossier du jeu)

Vérifie :
  1. En-têtes PARC (magic, tables, offsets)
  2. Cohérence de la table des dossiers (somme fichiers, ranges valides)
  3. Flags de compression SLLZ vs contenu réel
  4. Décompression SLLZ de chaque fichier compressé
  5. Taille u_sz vs taille décompressée
  6. Fichiers critiques (pac_STID_ST_KAMURO.bin, uid0104006f.msg, etc.)
"""

import os
import sys
import struct
import time

# ── SLLZ Decompressor (self-contained, proven Sega bit-flag format) ─────────
def decompress_sllz(data):
    """Decompress SLLZ-compressed data (Sega/RGG bit-flag format)."""
    import io as _io
    if len(data) < 16 or data[:4] != b'SLLZ':
        raise ValueError("Not SLLZ data")
    endian_byte = data[4]
    endian = '<' if endian_byte == 0 else '>'
    version, header_size = struct.unpack(endian + 'BH', data[5:8])
    uncomp_size, comp_size = struct.unpack(endian + 'II', data[8:16])

    inp = _io.BytesIO(data[header_size:])
    out = _io.BytesIO()

    cur_val = inp.read(1)[0]
    bit_count = 8

    def get_flag():
        nonlocal cur_val, bit_count
        res = (cur_val & 0x80) != 0
        bit_count -= 1
        cur_val = (cur_val << 1) & 0xFF
        if bit_count == 0:
            b = inp.read(1)
            if b:
                cur_val = b[0]
            bit_count = 8
        return res

    while out.tell() < uncomp_size and inp.tell() < len(data) - header_size:
        is_copy = get_flag()
        if not is_copy:
            b = inp.read(1)
            if not b:
                break
            out.write(b)
        else:
            cf_bytes = inp.read(2)
            if len(cf_bytes) < 2:
                break
            copy_flags = cf_bytes[0] | (cf_bytes[1] << 8)
            copy_dist = 1 + (copy_flags >> 4)
            copy_count = 3 + (copy_flags & 0xF)

            curr_pos = out.tell()
            out.seek(curr_pos - copy_dist)
            block = out.read(copy_count)
            while len(block) < copy_count:
                out.seek(curr_pos - copy_dist)
                block += out.read(copy_count - len(block))
            out.seek(curr_pos)
            out.write(block)

    return out.getvalue()


# ── PAR Archive Validator ───────────────────────────────────────────────────
class ParValidator:
    def __init__(self, path):
        self.path = path
        self.basename = os.path.basename(path)
        self.issues = []
        self.warnings = []
        self.file_count = 0
        self.folder_count = 0

    def error(self, msg):
        self.issues.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def validate(self):
        try:
            with open(self.path, 'rb') as f:
                self.data = f.read()
        except Exception as ex:
            self.error(f"Impossible de lire le fichier: {ex}")
            return

        if len(self.data) < 32:
            self.error(f"Fichier trop petit ({len(self.data)} octets)")
            return

        # 1. Magic
        magic = struct.unpack('>I', self.data[:4])[0]
        if magic != 0x50415243:
            self.error(f"Magic invalide: {hex(magic)} (attendu: 0x50415243)")
            return

        # 2. Header
        self.folder_count, self.folder_table_off, self.file_count, self.file_table_off = \
            struct.unpack('>4I', self.data[16:32])

        if self.folder_table_off >= len(self.data):
            self.error(f"Offset table dossiers hors limites: {hex(self.folder_table_off)}")
            return
        if self.file_table_off >= len(self.data):
            self.error(f"Offset table fichiers hors limites: {hex(self.file_table_off)}")
            return

        # 3. Folder Table
        self._check_folders()

        # 4. File Entries
        self._check_files()

    def _check_folders(self):
        total_files_in_folders = 0
        for i in range(self.folder_count):
            e_off = self.folder_table_off + i * 32
            if e_off + 32 > len(self.data):
                self.error(f"Dossier [{i}]: entrée dépasse la taille de l'archive")
                continue
            fields = struct.unpack('>8I', self.data[e_off : e_off + 32])
            f_name_off = 32 + i * 64
            fname = self.data[f_name_off : f_name_off + 64].split(b'\x00')[0].decode('latin1', 'replace')

            sub_count = fields[0]       # nombre de sous-dossiers ou type
            parent_id = fields[1]       # parent ou identifiant
            f_file_count = fields[2]    # nombre de fichiers dans ce dossier
            f_start_idx = fields[3]     # index du premier fichier

            total_files_in_folders += f_file_count

            if f_start_idx + f_file_count > self.file_count:
                self.error(
                    f"Dossier [{i}] '{fname}': plage fichiers [{f_start_idx}..{f_start_idx + f_file_count - 1}] "
                    f"dépasse file_count={self.file_count}"
                )

        if total_files_in_folders != self.file_count:
            self.error(
                f"Somme fichiers des dossiers ({total_files_in_folders}) != file_count ({self.file_count})"
            )

    def _check_files(self):
        name_offset = 32 + self.folder_count * 64

        for i in range(self.file_count):
            e_off = self.file_table_off + i * 32
            if e_off + 32 > len(self.data):
                self.error(f"Fichier [{i}]: entrée hors limites")
                break

            flags, u_sz, c_sz, f_off = struct.unpack('>4I', self.data[e_off : e_off + 16])
            n_off = name_offset + i * 64
            fn = self.data[n_off : n_off + 64].split(b'\x00')[0].decode('latin1', 'replace')

            # Bounds check
            if f_off + c_sz > len(self.data):
                self.error(f"{fn}: données dépassent l'archive (off={hex(f_off)}, sz={c_sz}, total={len(self.data)})")
                continue

            file_bytes = self.data[f_off : f_off + c_sz]

            # SLLZ coherence
            is_sllz_flag = bool(flags & 0x80000000)
            is_sllz_data = file_bytes[:4] == b'SLLZ'

            if is_sllz_flag and not is_sllz_data:
                self.error(f"{fn}: flag=COMPRESSÉ mais données ne commencent pas par SLLZ")
            elif not is_sllz_flag and is_sllz_data:
                self.error(f"{fn}: flag=NON-COMPRESSÉ mais données commencent par SLLZ")

            # Size coherence for uncompressed
            if not is_sllz_flag:
                if c_sz != u_sz:
                    self.warn(f"{fn}: non-compressé mais c_sz({c_sz}) != u_sz({u_sz})")

            # Decompress test
            if is_sllz_flag and is_sllz_data:
                try:
                    dec = decompress_sllz(file_bytes)
                    if len(dec) != u_sz:
                        self.error(
                            f"{fn}: taille décompressée {len(dec)} != u_sz attendu {u_sz}"
                        )
                except Exception as ex:
                    self.error(f"{fn}: ERREUR décompression SLLZ: {ex}")

            # ── Critical file checks ──
            if fn == 'pac_STID_ST_KAMURO.bin':
                if u_sz != 1233900:
                    self.error(
                        f"{fn}: taille incorrecte {u_sz} (attendu: 1233900) — "
                        f"CAUSE CONNUE DU CRASH DEVANT DON QUIJOTE"
                    )
                if not is_sllz_flag:
                    self.error(f"{fn}: devrait être compressé SLLZ")

            if fn == 'uid0104006f.msg':
                if is_sllz_flag and is_sllz_data:
                    try:
                        dec = decompress_sllz(file_bytes)
                        if b'Pourquoi font-ils la queue' not in dec and b"What's this line for" not in dec:
                            self.warn(f"{fn}: texte de la quête Don Quijote non trouvé")
                    except:
                        pass

            if fn == 'uid033317da.msg':
                if u_sz != 7245:
                    self.error(
                        f"{fn}: taille incorrecte {u_sz} (attendu: 7245) — "
                        f"CAUSE DU SOFTLOCK DES CABINES TÉLÉPHONIQUES"
                    )
                if not is_sllz_flag:
                    self.error(f"{fn}: devrait être compressé SLLZ")
                if is_sllz_flag and is_sllz_data:
                    try:
                        dec = decompress_sllz(file_bytes)
                        if b'Sauvegardez et utilisez le coffre' not in dec:
                            self.warn(f"{fn}: texte français des cabines non trouvé")
                    except:
                        pass


# ── Main ────────────────────────────────────────────────────────────────────
def find_game_dir(hint=None):
    """Locate the Yakuza 0 data directory."""
    candidates = []
    if hint:
        candidates.append(hint)
        candidates.append(os.path.join(hint, 'data'))
    
    # Try relative paths
    candidates.append('release_gog/data')
    candidates.append('release_gog')
    candidates.append('data')
    candidates.append('.')

    for c in candidates:
        if os.path.isdir(c):
            # Check if it has the expected structure
            if os.path.isdir(os.path.join(c, 'wdr_par_c')) or os.path.isdir(os.path.join(c, 'bootpar')):
                return c
            # Maybe c IS the game root, check c/data
            sub = os.path.join(c, 'data')
            if os.path.isdir(sub) and (os.path.isdir(os.path.join(sub, 'wdr_par_c')) or os.path.isdir(os.path.join(sub, 'bootpar'))):
                return sub
    return None


def find_all_pars(data_dir):
    """Find all .par files recursively."""
    pars = []
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if f.endswith('.par'):
                pars.append(os.path.join(root, f))
    return sorted(pars)


def main():
    print("=" * 70)
    print("  VÉRIFICATEUR D'INTÉGRITÉ — Patch FR Yakuza 0 GOG")
    print("=" * 70)
    print()

    hint = sys.argv[1] if len(sys.argv) > 1 else None
    data_dir = find_game_dir(hint)

    if not data_dir:
        print("[ERREUR] Impossible de trouver le dossier data/ du jeu.")
        print("Usage: python3 verify_patch.py /chemin/vers/Yakuza0/")
        sys.exit(1)

    print(f"[*] Dossier data détecté: {os.path.abspath(data_dir)}")
    all_pars = find_all_pars(data_dir)
    print(f"[*] {len(all_pars)} archives .par trouvées")
    print()

    # Classify
    critical_names = {
        'boot.par', 'stay.par', 'common.par', 'wdr.par',
        'pause.par', 'chapter.par', 'minigame.par', 'find_arms.par',
        'pokecir.par'
    }

    critical_pars = [p for p in all_pars if os.path.basename(p) in critical_names]
    other_pars = [p for p in all_pars if os.path.basename(p) not in critical_names]

    total_pass = 0
    total_fail = 0
    total_warn = 0
    all_results = []

    start = time.time()

    # 1. Critical archives (deep check with SLLZ decompression)
    print("─" * 70)
    print("  VÉRIFICATION APPROFONDIE DES ARCHIVES CRITIQUES (avec décompression)")
    print("─" * 70)
    for p in critical_pars:
        rel = os.path.relpath(p, data_dir)
        v = ParValidator(p)
        v.validate()

        if v.issues:
            total_fail += 1
            status = "\033[91m[ÉCHEC]\033[0m"
            print(f"  {status} {rel}")
            for e in v.issues:
                print(f"         ❌ {e}")
            for w in v.warnings:
                print(f"         ⚠️  {w}")
        elif v.warnings:
            total_warn += 1
            total_pass += 1
            status = "\033[93m[AVERT]\033[0m"
            print(f"  {status} {rel}")
            for w in v.warnings:
                print(f"         ⚠️  {w}")
        else:
            total_pass += 1
            status = "\033[92m[  OK ]\033[0m"
            print(f"  {status} {rel} ({v.file_count} fichiers)")

        all_results.append((rel, v))

    # 2. Other archives (structural check only — skip SLLZ decompression for speed)
    print()
    print("─" * 70)
    print("  VÉRIFICATION STRUCTURELLE DES AUTRES ARCHIVES")
    print("─" * 70)

    other_fail = 0
    other_pass = 0
    for p in other_pars:
        rel = os.path.relpath(p, data_dir)
        try:
            with open(p, 'rb') as f:
                data = f.read()
            magic = struct.unpack('>I', data[:4])[0]
            if magic != 0x50415243:
                print(f"  \033[91m[ÉCHEC]\033[0m {rel}: magic invalide {hex(magic)}")
                other_fail += 1
                continue

            fc, fto, flc, flto = struct.unpack('>4I', data[16:32])
            name_offset = 32 + fc * 64

            has_issue = False
            for i in range(flc):
                e_off = flto + i * 32
                flags, u_sz, c_sz, f_off = struct.unpack('>4I', data[e_off : e_off + 16])
                if f_off + c_sz > len(data):
                    n_off = name_offset + i * 64
                    fn = data[n_off : n_off + 64].split(b'\x00')[0].decode('latin1', 'replace')
                    print(f"  \033[91m[ÉCHEC]\033[0m {rel}: {fn} dépasse l'archive")
                    has_issue = True
                    break
                fb = data[f_off : f_off + min(c_sz, 4)]
                if (flags & 0x80000000) and fb[:4] != b'SLLZ':
                    n_off = name_offset + i * 64
                    fn = data[n_off : n_off + 64].split(b'\x00')[0].decode('latin1', 'replace')
                    print(f"  \033[91m[ÉCHEC]\033[0m {rel}: {fn} flag SLLZ incohérent")
                    has_issue = True
                    break

            if has_issue:
                other_fail += 1
            else:
                other_pass += 1
        except Exception as ex:
            print(f"  \033[91m[ÉCHEC]\033[0m {rel}: {ex}")
            other_fail += 1

    total_pass += other_pass
    total_fail += other_fail

    elapsed = time.time() - start

    # Summary
    print()
    print("=" * 70)
    print("  RÉSUMÉ")
    print("=" * 70)
    print(f"  Archives vérifiées : {total_pass + total_fail}")
    print(f"  ✅ OK              : {total_pass}")
    if total_warn:
        print(f"  ⚠️  Avertissements  : {total_warn}")
    print(f"  ❌ Échecs          : {total_fail}")
    print(f"  ⏱️  Durée           : {elapsed:.1f}s")
    print()

    if total_fail == 0:
        print("  \033[92m╔══════════════════════════════════════════════════════════╗\033[0m")
        print("  \033[92m║  TOUTES LES ARCHIVES SONT SAINES — PATCH PRÊT À JOUER  ║\033[0m")
        print("  \033[92m╚══════════════════════════════════════════════════════════╝\033[0m")
    else:
        print("  \033[91m╔══════════════════════════════════════════════════════════╗\033[0m")
        print("  \033[91m║  ATTENTION : DES PROBLÈMES ONT ÉTÉ DÉTECTÉS !          ║\033[0m")
        print("  \033[91m╚══════════════════════════════════════════════════════════╝\033[0m")
        print()
        print("  Vérifiez les erreurs ci-dessus et réappliquez le patch si nécessaire.")

    print()
    return 0 if total_fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

import struct
import os

def unpack_par(par_path, extract_names=['hd_hankaku.dds', 'hd2_hankaku.dds']):
    with open(par_path, 'rb') as f:
        magic, unkA, unkB, unkC = struct.unpack('>4I', f.read(16))
        assert magic == 0x50415243, "Not PARC"
        folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', f.read(16))
        folder_names_offset = 32
        file_names_offset = folder_names_offset + folder_count * 64
        
        print(f"Folders: {folder_count}, Files: {file_count}")
        
        for i in range(file_count):
            f.seek(file_names_offset + i * 64)
            name_bytes = f.read(64)
            name = name_bytes.split(b'\x00')[0].decode('latin1', errors='ignore')
            
            f.seek(file_table_offset + i * 32)
            flags, uncomp_size, comp_size, offset, unkE, unkF, unkG, unkH = struct.unpack('>8I', f.read(32))
            
            if name in extract_names or not extract_names:
                print(f"File: {name}, flags={hex(flags)}, comp_size={comp_size}, uncomp_size={uncomp_size}, offset={hex(offset)}")
                f.seek(offset)
                data = f.read(comp_size)
                out_path = os.path.join('scratch', name)
                with open(out_path, 'wb') as out_f:
                    out_f.write(data)
                print(f"Extracted to {out_path} ({len(data)} bytes)")

if __name__ == '__main__':
    unpack_par('staging_gog_patch/Yakuza 0 Patch Vostfr by RGG Yakuza Rev 1.10/data/fontpar/font.par')

import struct
import io

def decompress_sllz(compressed_data):
    # Header:
    # 0x00: Magic 'SLLZ' (4 bytes)
    # 0x04: Endianness (1 byte: 0 = LE, 1 = BE)
    # 0x05: Version (1 byte)
    # 0x06: HeaderSize (2 bytes)
    # 0x08: UncompressedSize (4 bytes)
    # 0x0C: CompressedSize (4 bytes)
    magic = compressed_data[:4]
    assert magic == b'SLLZ', f"Not SLLZ: {magic}"
    endian_byte = compressed_data[4]
    endian = '<' if endian_byte == 0 else '>'
    version, header_size = struct.unpack(endian + 'BH', compressed_data[5:8])
    uncomp_size, comp_size = struct.unpack(endian + 'II', compressed_data[8:16])
    
    # BitManager
    inp = io.BytesIO(compressed_data[header_size:])
    out = io.BytesIO()
    
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
    
    while out.tell() < uncomp_size and inp.tell() < len(compressed_data) - header_size:
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
            # In case copy_count > copy_dist (RLE)
            while len(block) < copy_count:
                out.seek(curr_pos - copy_dist)
                block += out.read(copy_count - len(block))
            out.seek(curr_pos)
            out.write(block)
            
    return out.getvalue()

def extract_file(par_path, target_name):
    with open(par_path, 'rb') as f:
        magic, unkA, unkB, unkC = struct.unpack('>4I', f.read(16))
        folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', f.read(16))
        folder_names_offset = 32
        file_names_offset = folder_names_offset + folder_count * 64
        for i in range(file_count):
            f.seek(file_names_offset + i * 64)
            name = f.read(64).split(b'\x00')[0].decode('latin1', errors='ignore')
            if name == target_name:
                f.seek(file_table_offset + i * 32)
                flags, uncomp_size, comp_size, offset = struct.unpack('>4I', f.read(16))
                f.seek(offset)
                raw = f.read(comp_size)
                if flags & 0x80000000:
                    data = decompress_sllz(raw)
                else:
                    data = raw
                return data
    return None

if __name__ == '__main__':
    for f in ['complete_select.bin_c', 'complete_minigame.bin_c']:
        data = extract_file('release_gog/data/pausepar_e/pause.par', f)
        if data:
            print(f'{f}: {len(data)} bytes')
            import re
            strings = re.findall(b'[a-zA-Z0-9_\\s\\-:\\.]{3,}', data)
            print('Strings:', [s.decode(errors='ignore') for s in strings[:15]])

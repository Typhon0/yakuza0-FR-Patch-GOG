import struct
import io

SEARCH_SIZE = 4096
MAX_LENGTH = 18

class MatchResult:
    def __init__(self, found=False, distance=0, length=1):
        self.found = found
        self.distance = distance
        self.length = length

class SllzItem:
    def __init__(self, is_literal, literal=0, copy_flags=0):
        self.is_literal = is_literal
        self.literal = literal
        self.copy_flags = copy_flags

class BitManager:
    def __init__(self, output):
        self.output = output
        self.current_value = 0
        self.bit_count = 0
        self.is_byte_change = False

    def flush(self):
        self.output.write(bytes([self.current_value]))
        self.current_value = 0
        self.bit_count = 0
        self.is_byte_change = True

    def set_flag(self, val):
        self.is_byte_change = False
        if val == 1:
            self.current_value |= (1 << (7 - self.bit_count))
        self.bit_count += 1
        if self.bit_count == 8:
            self.flush()

def find_match(input_data, read_pos):
    current = read_pos - 1
    best_pos = 0
    best_length = 0
    
    start_pos = max(read_pos - SEARCH_SIZE, 0)
    
    while current >= start_pos:
        if input_data[current] == input_data[read_pos]:
            max_len = min(len(input_data) - read_pos, MAX_LENGTH)
            max_len = min(max_len, read_pos - current)
            
            length = 1
            while length < max_len and input_data[current + length] == input_data[read_pos + length]:
                length += 1
                
            if length > best_length:
                best_length = length
                best_pos = current
                if best_length == MAX_LENGTH:
                    break
        current -= 1

    if best_length >= 3:
        return MatchResult(True, read_pos - best_pos, best_length)
    else:
        return MatchResult(False, 0, 1)

def decompress_sllz(compressed_data):
    magic = compressed_data[:4]
    assert magic == b'SLLZ', f"Not SLLZ: {magic}"
    endian_byte = compressed_data[4]
    endian = '<' if endian_byte == 0 else '>'
    version, header_size = struct.unpack(endian + 'BH', compressed_data[5:8])
    uncomp_size, comp_size = struct.unpack(endian + 'II', compressed_data[8:16])
    
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
            while len(block) < copy_count:
                out.seek(curr_pos - copy_dist)
                block += out.read(copy_count - len(block))
            out.seek(curr_pos)
            out.write(block)
            
    return out.getvalue()

from collections import defaultdict

def compress_sllz(uncompressed_data):
    output = io.BytesIO()
    output.write(b'SLLZ\x00\x01\x10\x00')
    output.write(struct.pack('<I', len(uncompressed_data)))
    output.write(struct.pack('<I', 0))
    
    manager = BitManager(output)
    queue = []
    items_to_write = 7
    current_position = 0
    uncompressed_size = len(uncompressed_data)
    
    pos_heads = defaultdict(list)
    
    while current_position < uncompressed_size:
        best_pos = 0
        best_length = 0
        
        if current_position + 3 <= uncompressed_size:
            triplet = uncompressed_data[current_position : current_position + 3]
            candidates = pos_heads[triplet]
            start_pos = max(0, current_position - SEARCH_SIZE)
            
            for cand in reversed(candidates[-32:]):
                if cand < start_pos:
                    break
                max_len = min(uncompressed_size - current_position, MAX_LENGTH)
                max_len = min(max_len, current_position - cand)
                
                l = 3
                while l < max_len and uncompressed_data[cand + l] == uncompressed_data[current_position + l]:
                    l += 1
                if l > best_length:
                    best_length = l
                    best_pos = cand
                    if best_length == MAX_LENGTH:
                        break
                        
        if best_length >= 3:
            match = MatchResult(True, current_position - best_pos, best_length)
        else:
            match = MatchResult(False, 0, 1)
            
        if not match.found:
            queue.append(SllzItem(True, literal=uncompressed_data[current_position]))
            manager.set_flag(0)
            if current_position + 3 <= uncompressed_size:
                pos_heads[uncompressed_data[current_position : current_position + 3]].append(current_position)
            current_position += 1
        else:
            copy_count = (match.length - 3) & 0x0F
            copy_distance = ((match.distance - 1) << 4) & 0xFFFF
            tuple_val = copy_distance | copy_count
            queue.append(SllzItem(False, copy_flags=tuple_val))
            manager.set_flag(1)
            for p in range(current_position, min(current_position + match.length, uncompressed_size - 2)):
                pos_heads[uncompressed_data[p : p + 3]].append(p)
            current_position += match.length
            
        if manager.is_byte_change:
            for _ in range(items_to_write):
                item = queue.pop(0)
                if item.is_literal:
                    output.write(bytes([item.literal]))
                else:
                    output.write(struct.pack('<H', item.copy_flags))
            items_to_write = 8
            
    manager.flush()
    while queue:
        item = queue.pop(0)
        if item.is_literal:
            output.write(bytes([item.literal]))
        else:
            output.write(struct.pack('<H', item.copy_flags))
            
    compressed_bytes = bytearray(output.getvalue())
    total_len = len(compressed_bytes)
    struct.pack_into('<I', compressed_bytes, 12, total_len)
    return bytes(compressed_bytes)

if __name__ == '__main__':
    # Test roundtrip
    test_cases = [
        b"Hello world!",
        b"A" * 100,
        b"The quick brown fox jumps over the lazy dog." * 20
    ]
    for tc in test_cases:
        comp = compress_sllz(tc)
        decomp = decompress_sllz(comp)
        assert decomp == tc, f"Failed roundtrip for {len(tc)} bytes"
        print(f"Passed: {len(tc)} bytes -> {len(comp)} bytes")
    print("ALL TESTS PASSED SUCCESSFULLY!")

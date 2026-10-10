mod table_catalog;

use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

// ============================================================================
// 1. Native SLLZ Decompressor (Zero Dependencies)
// ============================================================================
fn decompress_sllz(data: &[u8]) -> Vec<u8> {
    if data.len() < 16 || &data[0..4] != b"SLLZ" {
        return data.to_vec();
    }
    let is_little = data[4] == 0;
    let header_size = if is_little {
        u16::from_le_bytes([data[6], data[7]]) as usize
    } else {
        u16::from_be_bytes([data[6], data[7]]) as usize
    };
    let uncomp_size = if is_little {
        u32::from_le_bytes([data[8], data[9], data[10], data[11]]) as usize
    } else {
        u32::from_be_bytes([data[8], data[9], data[10], data[11]]) as usize
    };

    let mut out = Vec::with_capacity(uncomp_size);
    let mut in_pos = header_size;
    if in_pos >= data.len() {
        return out;
    }

    let mut cur_val = data[in_pos];
    in_pos += 1;
    let mut bit_count = 8;

    while out.len() < uncomp_size && in_pos <= data.len() {
        let is_copy = (cur_val & 0x80) != 0;
        bit_count -= 1;
        cur_val = (cur_val << 1) & 0xFF;
        if bit_count == 0 {
            if in_pos < data.len() {
                cur_val = data[in_pos];
                in_pos += 1;
            }
            bit_count = 8;
        }

        if !is_copy {
            if in_pos <= data.len() {
                let b = data[in_pos];
                in_pos += 1;
                out.push(b);
            } else {
                break;
            }
        } else {
            if in_pos + 1 >= data.len() {
                break;
            }
            let b0 = data[in_pos] as usize;
            let b1 = data[in_pos + 1] as usize;
            in_pos += 2;
            let copy_flags = b0 | (b1 << 8);
            let copy_dist = 1 + (copy_flags >> 4);
            let copy_count = 3 + (copy_flags & 0x0F);

            if copy_dist > out.len() {
                break;
            }
            for _ in 0..copy_count {
                if out.len() >= uncomp_size {
                    break;
                }
                let src_pos = out.len() - copy_dist;
                let b = out[src_pos];
                out.push(b);
            }
        }
    }
    out
}

// ============================================================================
// 2. PAR Archive Parser & Gap Calculator
// ============================================================================
#[derive(Clone, Debug)]
struct ParEntry {
    name: String,
    flags: u32,
    uncomp_size: u32,
    comp_size: u32,
    offset: u32,
    available_gap: u32,
}

fn parse_par(bytes: &[u8]) -> Option<Vec<ParEntry>> {
    if bytes.len() < 32 || &bytes[0..4] != b"PARC" {
        return None;
    }
    let folder_count = u32::from_be_bytes([bytes[16], bytes[17], bytes[18], bytes[19]]) as usize;
    let file_count = u32::from_be_bytes([bytes[24], bytes[25], bytes[26], bytes[27]]) as usize;
    let file_table_offset = u32::from_be_bytes([bytes[28], bytes[29], bytes[30], bytes[31]]) as usize;
    let name_offset = 32 + folder_count * 64;

    let mut entries = Vec::with_capacity(file_count);
    for i in 0..file_count {
        let n_start = name_offset + i * 64;
        if n_start + 64 > bytes.len() {
            break;
        }
        let n_slice = &bytes[n_start..n_start + 64];
        let name_end = n_slice.iter().position(|&b| b == 0).unwrap_or(64);
        let name = String::from_utf8_lossy(&n_slice[..name_end]).to_string();

        let e_start = file_table_offset + i * 32;
        if e_start + 16 > bytes.len() {
            break;
        }
        let flags = u32::from_be_bytes([bytes[e_start], bytes[e_start + 1], bytes[e_start + 2], bytes[e_start + 3]]);
        let uncomp_size = u32::from_be_bytes([bytes[e_start + 4], bytes[e_start + 5], bytes[e_start + 6], bytes[e_start + 7]]);
        let comp_size = u32::from_be_bytes([bytes[e_start + 8], bytes[e_start + 9], bytes[e_start + 10], bytes[e_start + 11]]);
        let offset = u32::from_be_bytes([bytes[e_start + 12], bytes[e_start + 13], bytes[e_start + 14], bytes[e_start + 15]]);

        entries.push(ParEntry {
            name,
            flags,
            uncomp_size,
            comp_size,
            offset,
            available_gap: 0,
        });
    }

    // Sort by offset to compute available sector gaps
    let mut indices: Vec<usize> = (0..entries.len()).collect();
    indices.sort_by_key(|&idx| entries[idx].offset);

    for i in 0..indices.len() {
        let cur_idx = indices[i];
        let cur_off = entries[cur_idx].offset;
        let next_off = if i + 1 < indices.len() {
            entries[indices[i + 1]].offset
        } else {
            bytes.len() as u32
        };
        entries[cur_idx].available_gap = if next_off >= cur_off { next_off - cur_off } else { 0 };
    }

    Some(entries)
}

// ============================================================================
// 3. Sega RGG Binary Property Table Simulator (0x20070319)
// ============================================================================
#[derive(Clone, Debug)]
struct ColDesc {
    name: String,
    col_type: u32,
    count: u32,
    size: u32,
    data_start: usize,
}

#[derive(Clone, Debug)]
struct ParsedTable {
    is_big_endian: bool,
    num_cols: usize,
    num_rows: usize,
    cols: Vec<ColDesc>,
    data: Vec<u8>,
}

#[derive(Clone, Debug)]
struct TableIssue {
    file: String,
    severity: String,
    message: String,
}

fn parse_rgg_table(data: &[u8]) -> Option<ParsedTable> {
    if data.len() < 16 {
        return None;
    }
    let magic_le = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    let is_rgg = magic_le == 0x20070319 || &data[0..4] == b"\x20\x07\x03\x19";
    if !is_rgg {
        return None;
    }
    let is_big_endian = &data[0..4] == b"\x20\x07\x03\x19";
    let (num_cols, num_rows) = if is_big_endian {
        (
            u32::from_be_bytes([data[4], data[5], data[6], data[7]]) as usize,
            u32::from_be_bytes([data[8], data[9], data[10], data[11]]) as usize,
        )
    } else {
        (
            u32::from_le_bytes([data[4], data[5], data[6], data[7]]) as usize,
            u32::from_le_bytes([data[8], data[9], data[10], data[11]]) as usize,
        )
    };

    let col_table_size = 16 + num_cols * 64;
    if data.len() < col_table_size {
        return None;
    }

    let mut cols = Vec::with_capacity(num_cols);
    let mut curr_data_off = col_table_size;

    for c in 0..num_cols {
        let col_off = 16 + c * 64;
        let c_slice = &data[col_off..col_off + 32];
        let name_end = c_slice.iter().position(|&b| b == 0).unwrap_or(32);
        let name = String::from_utf8_lossy(&c_slice[..name_end]).to_string();

        let (col_type, count, size) = if is_big_endian {
            (
                u32::from_be_bytes([data[col_off + 48], data[col_off + 49], data[col_off + 50], data[col_off + 51]]),
                u32::from_be_bytes([data[col_off + 52], data[col_off + 53], data[col_off + 54], data[col_off + 55]]),
                u32::from_be_bytes([data[col_off + 56], data[col_off + 57], data[col_off + 58], data[col_off + 59]]),
            )
        } else {
            (
                u32::from_le_bytes([data[col_off + 48], data[col_off + 49], data[col_off + 50], data[col_off + 51]]),
                u32::from_le_bytes([data[col_off + 52], data[col_off + 53], data[col_off + 54], data[col_off + 55]]),
                u32::from_le_bytes([data[col_off + 56], data[col_off + 57], data[col_off + 58], data[col_off + 59]]),
            )
        };

        cols.push(ColDesc {
            name,
            col_type,
            count,
            size,
            data_start: curr_data_off,
        });
        curr_data_off += size as usize;
    }

    Some(ParsedTable {
        is_big_endian,
        num_cols,
        num_rows,
        cols,
        data: data.to_vec(),
    })
}

fn simulate_rgg_table(file_name: &str, table: &ParsedTable) -> Vec<TableIssue> {
    let mut issues = Vec::new();
    let data = &table.data;

    let mut expected_payload = 16 + table.num_cols * 64;
    for c in &table.cols {
        expected_payload += c.size as usize;
    }
    if expected_payload != data.len() {
        issues.push(TableIssue {
            file: file_name.to_string(),
            severity: "WARNING".to_string(),
            message: format!("Taille de payload calculée ({}) != taille réelle ({})", expected_payload, data.len()),
        });
    }

    // 1. Simulate ConvertEndianness Type 2 loop (Crash 0x14037177C)
    if table.is_big_endian {
        for (idx, c) in table.cols.iter().enumerate() {
            if c.col_type == 2 {
                let start = c.data_start;
                let end = start + c.size as usize;
                if end > data.len() {
                    issues.push(TableIssue {
                        file: file_name.to_string(),
                        severity: "FATAL".to_string(),
                        message: format!("Col {} ({}) Type 2 dépasse la fin de fichier", idx, c.name),
                    });
                    continue;
                }
                let mut pos = start;
                for i in 0..c.count {
                    if pos + 2 > end {
                        issues.push(TableIssue {
                            file: file_name.to_string(),
                            severity: "FATAL".to_string(),
                            message: format!("Col {} ({}) item {}/{} : lecture mot ID 16-bit hors limites (Crash 0x37177C)", idx, c.name, i, c.count),
                        });
                        break;
                    }
                    pos += 2;
                    while pos < end && data[pos] != 0 {
                        pos += 1;
                    }
                    if pos >= end {
                        issues.push(TableIssue {
                            file: file_name.to_string(),
                            severity: "FATAL".to_string(),
                            message: format!("Col {} ({}) item {}/{} : terminateur nul \\x00 manquant (Crash 0x37177C)", idx, c.name, i, c.count),
                        });
                        break;
                    }
                    pos += 1;
                }
            }
        }
    }

    // 2. Simulate BuildColumnIndex (Crash 0x1403711DB & 0x140371324)
    for (idx, c) in table.cols.iter().enumerate() {
        if c.col_type <= 5 || c.col_type == 8 {
            if c.data_start + c.size as usize > data.len() {
                issues.push(TableIssue {
                    file: file_name.to_string(),
                    severity: "FATAL".to_string(),
                    message: format!("Col {} ({}) data_start + size dépasse le buffer", idx, c.name),
                });
                continue;
            }

            if c.col_type == 0 {
                let col_data = &data[c.data_start..c.data_start + c.size as usize];
                let nulls = col_data.iter().filter(|&&b| b == 0).count();
                if nulls < table.num_rows {
                    issues.push(TableIssue {
                        file: file_name.to_string(),
                        severity: "FATAL".to_string(),
                        message: format!("Col {} ({}) Type 0 : {} octets nuls trouvés < {} lignes attendues (Crash 0x3711DB)", idx, c.name, nulls, table.num_rows),
                    });
                }
            }
        }
    }

    issues
}

// ============================================================================
// 4. Native PE Executable Parser for Yakuza0.exe (Zero external tools)
// ============================================================================
struct PeSection {
    _name: String,
    virtual_address: u32,
    _virtual_size: u32,
    raw_ptr: u32,
    raw_size: u32,
}

struct PeFile {
    _image_base: u64,
    sections: Vec<PeSection>,
    data: Vec<u8>,
}

impl PeFile {
    fn load(path: &Path) -> Option<Self> {
        let bytes = fs::read(path).ok()?;
        if bytes.len() < 0x200 || &bytes[0..2] != b"MZ" {
            return None;
        }
        let e_lfanew = u32::from_le_bytes([bytes[0x3C], bytes[0x3D], bytes[0x3E], bytes[0x3F]]) as usize;
        if e_lfanew + 24 > bytes.len() || &bytes[e_lfanew..e_lfanew + 4] != b"PE\0\0" {
            return None;
        }
        let coff = e_lfanew + 4;
        let num_sections = u16::from_le_bytes([bytes[coff + 2], bytes[coff + 3]]) as usize;
        let opt_size = u16::from_le_bytes([bytes[coff + 16], bytes[coff + 17]]) as usize;
        let opt = coff + 20;
        if opt + opt_size > bytes.len() {
            return None;
        }
        let magic = u16::from_le_bytes([bytes[opt], bytes[opt + 1]]);
        let _image_base = if magic == 0x20b {
            u64::from_le_bytes([
                bytes[opt + 24], bytes[opt + 25], bytes[opt + 26], bytes[opt + 27],
                bytes[opt + 28], bytes[opt + 29], bytes[opt + 30], bytes[opt + 31],
            ])
        } else {
            u32::from_le_bytes([bytes[opt + 28], bytes[opt + 29], bytes[opt + 30], bytes[opt + 31]]) as u64
        };
        let sec_start = opt + opt_size;
        let mut sections = Vec::with_capacity(num_sections);
        for i in 0..num_sections {
            let s = sec_start + i * 40;
            if s + 40 > bytes.len() {
                break;
            }
            let name_slice = &bytes[s..s + 8];
            let name_end = name_slice.iter().position(|&b| b == 0).unwrap_or(8);
            let _name = String::from_utf8_lossy(&name_slice[..name_end]).to_string();
            let _virtual_size = u32::from_le_bytes([bytes[s + 8], bytes[s + 9], bytes[s + 10], bytes[s + 11]]);
            let virtual_address = u32::from_le_bytes([bytes[s + 12], bytes[s + 13], bytes[s + 14], bytes[s + 15]]);
            let raw_size = u32::from_le_bytes([bytes[s + 16], bytes[s + 17], bytes[s + 18], bytes[s + 19]]);
            let raw_ptr = u32::from_le_bytes([bytes[s + 20], bytes[s + 21], bytes[s + 22], bytes[s + 23]]);
            sections.push(PeSection {
                _name,
                virtual_address,
                _virtual_size,
                raw_ptr,
                raw_size,
            });
        }
        Some(PeFile {
            _image_base,
            sections,
            data: bytes,
        })
    }

    fn rva_to_file_offset(&self, rva: u32) -> Option<usize> {
        for sec in &self.sections {
            if rva >= sec.virtual_address && rva < sec.virtual_address + sec.raw_size {
                return Some((rva - sec.virtual_address + sec.raw_ptr) as usize);
            }
        }
        None
    }

    fn read_bytes_at_rva(&self, rva: u32, len: usize) -> Option<&[u8]> {
        let off = self.rva_to_file_offset(rva)?;
        if off + len <= self.data.len() {
            Some(&self.data[off..off + len])
        } else {
            None
        }
    }
}

// ============================================================================
// 5. Game Engine Subsystem Resolver (Call Stack Decoder)
// ============================================================================
fn resolve_rva_symbol(rva: u32) -> &'static str {
    match rva {
        0x3711a0..=0x371330 => "CPropertyTable::BuildColumnIndex (Indexation colonnes/lignes)",
        0x370c30..=0x37119f => "CPropertyTable::Load (Chargement table binaire RGG)",
        0x371750..=0x371890 => "CPropertyTable::ConvertEndianness (Conversion type 2/bswap)",
        0x23400..=0x23700 => "SLLZ::Decompress (Décompresseur streaming sectoriel)",
        0xa4480..=0xa4650 => "CSoundWanderer::LoadResponse (Ambiance sonore / Wanderer)",
        0x6ea200..=0x6ea500 => "ScriptMessage::ExecuteBytecode (Lecteur dialogue .msg)",
        0x396700..=0x396850 => "TypewriterEffect::CountChars (Cabine téléphonique / Sauvegarde)",
        0x397000..=0x397150 => "FontRenderer::ApplyKerning (Crénage police Sega)",
        0x14f000..=0x150000 => "CCabaretClubSunshine::LaunchNight [CABARET SUNSHINE - NUIT]",
        0x22a000..=0x22c000 => "CPocketCircuit::InitStage [POCKET CIRCUIT]",
        0x32b000..=0x32c500 => "CBattleEncount::Init [COMBAT DE RUE / ENCOUNT]",
        _ => "Code Moteur Yakuza0.exe",
    }
}

fn collect_par_files(dir: &Path, list: &mut Vec<PathBuf>) {
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let p = entry.path();
            if p.is_dir() {
                collect_par_files(&p, list);
            } else if p.extension().map_or(false, |ext| ext == "par") {
                list.push(p);
            }
        }
    }
}

// ============================================================================
// 6. Preflight Engine Simulator (Multi-Threaded Ultra-Fast)
// ============================================================================
fn run_preflight(data_dir: &Path) {
    let start = Instant::now();
    println!("======================================================================");
    println!("  RGG PREFLIGHT SIMULATOR (RUST MULTI-THREAD) — Yakuza 0 GOG FR        ");
    println!("  Cible : {}", data_dir.display());
    println!("======================================================================\n");

    let mut par_files = Vec::new();
    collect_par_files(data_dir, &mut par_files);

    if par_files.is_empty() {
        println!("[-] Aucun fichier .par trouvé dans '{}'.", data_dir.display());
        return;
    }

    let num_threads = thread::available_parallelism().map(|n| n.get()).unwrap_or(4);
    println!("[*] Analyse multi-thread ({} threads) de {} archives .par en cours...\n", num_threads, par_files.len());

    let queue = Arc::new(Mutex::new(par_files));
    let mut handles = Vec::with_capacity(num_threads);

    for _ in 0..num_threads {
        let q = Arc::clone(&queue);
        handles.push(thread::spawn(move || {
            let mut local_files = 0;
            let mut local_tables = 0;
            let mut local_issues = Vec::new();

            loop {
                let par_path = {
                    let mut lock = q.lock().unwrap();
                    lock.pop()
                };
                let par_path = match par_path {
                    Some(p) => p,
                    None => break,
                };

                let bytes = match fs::read(&par_path) {
                    Ok(b) => b,
                    Err(_) => continue,
                };
                let entries = match parse_par(&bytes) {
                    Some(e) => e,
                    None => continue,
                };
                local_files += entries.len();
                let par_name = par_path.file_name().unwrap_or_default().to_string_lossy();

                for e in &entries {
                    if e.comp_size > e.available_gap && e.available_gap > 0 {
                        local_issues.push(TableIssue {
                            file: format!("{} -> {}", par_name, e.name),
                            severity: "FATAL".to_string(),
                            message: format!("Débordement sectoriel : comp_size {} > gap disponible {}", e.comp_size, e.available_gap),
                        });
                    }

                    if e.name == "response_wanderer.bin_c" && e.offset != 0x9a000 {
                        local_issues.push(TableIssue {
                            file: format!("{} -> {}", par_name, e.name),
                            severity: "FATAL".to_string(),
                            message: format!("Offset natif corrompu : offset 0x{:X} != 0x9a000 (Crash 0xA4526 garanti)", e.offset),
                        });
                    }

                    if (e.name == "uid00331696.msg" || e.name == "uid003316a2.msg") && e.uncomp_size != 27575 {
                        local_issues.push(TableIssue {
                            file: format!("{} -> {}", par_name, e.name),
                            severity: "FATAL".to_string(),
                            message: format!("Taille Bob Utsunomiya corrompue : {} != 27575 octets (Softlock garanti)", e.uncomp_size),
                        });
                    }

                    if e.name.ends_with(".bin_c") || e.name.ends_with(".bin") {
                        let raw_start = e.offset as usize;
                        let raw_end = raw_start + e.comp_size as usize;
                        if raw_end <= bytes.len() {
                            let raw_slice = &bytes[raw_start..raw_end];
                            let dec = if (e.flags & 0x80000000) != 0 || raw_slice.starts_with(b"SLLZ") {
                                decompress_sllz(raw_slice)
                            } else {
                                raw_slice.to_vec()
                            };

                            if let Some(tbl) = parse_rgg_table(&dec) {
                                local_tables += 1;
                                let issues = simulate_rgg_table(&format!("{} -> {}", par_name, e.name), &tbl);
                                local_issues.extend(issues);
                            }
                        }
                    }
                }
            }
            (local_files, local_tables, local_issues)
        }));
    }

    let mut total_files_scanned = 0;
    let mut total_tables_scanned = 0;
    let mut all_issues = Vec::new();

    for h in handles {
        if let Ok((f_count, t_count, issues)) = h.join() {
            total_files_scanned += f_count;
            total_tables_scanned += t_count;
            all_issues.extend(issues);
        }
    }

    let elapsed = start.elapsed();
    println!("----------------------------------------------------------------------");
    println!("  RÉSULTATS DE L'AUDIT PRÉVOL (MULTI-THREAD)");
    println!("----------------------------------------------------------------------");
    println!("  Archives scannées : {}", total_files_scanned);
    println!("  Tables RGG testées: {}", total_tables_scanned);
    println!("  Temps d'exécution : {:.2?}", elapsed);

    let fatal_count = all_issues.iter().filter(|i| i.severity == "FATAL").count();
    let warn_count = all_issues.iter().filter(|i| i.severity == "WARNING").count();

    if fatal_count == 0 && warn_count == 0 {
        println!("\n  [SUCCÈS TOTAL] TOUTES LES TABLES ET ARCHIVES SONT 100% VALIDES !");
        println!("  Aucun risque de crash de décalage mémoire détecté.");
    } else {
        println!("\n[!] Anomalies détectées ({} FATALES, {} AVERTISSEMENTS) :", fatal_count, warn_count);
        for i in &all_issues {
            println!("  [{}] {} : {}", i.severity, i.file, i.message);
        }
    }
    println!("======================================================================\n");
}

// ============================================================================
// 7. Instant Crash Analyzer (Sub-millisecond static catalog lookup)
// ============================================================================
fn resolve_log_path(given: &Path) -> PathBuf {
    if given.exists() {
        return given.to_path_buf();
    }
    let alts = [
        PathBuf::from("logs/crash.log"),
        PathBuf::from("crash.log"),
        PathBuf::from("crash/crash.log"),
    ];
    for a in &alts {
        if a.exists() {
            return a.clone();
        }
    }
    given.to_path_buf()
}

fn run_analyze(log_path: &Path, _data_dir: &Path, exe_path: &Path) {
    let start = Instant::now();
    let actual_log = resolve_log_path(log_path);

    println!("======================================================================");
    println!("  RGG CRASH ANALYZER (RUST ULTRA-PERFORMANCE) — Yakuza 0 GOG FR        ");
    println!("  Log : {}", actual_log.display());
    println!("======================================================================\n");

    let content = match fs::read_to_string(&actual_log) {
        Ok(c) => c,
        Err(_) => {
            println!("[-] Impossible de lire le fichier log '{}'.", actual_log.display());
            return;
        }
    };

    let blocks: Vec<&str> = content.split("Unhandled Top-Level Exception").collect();
    if blocks.len() < 2 {
        println!("[-] Aucun bloc d'exception récent trouvé dans '{}'.", actual_log.display());
        return;
    }

    let last_block = blocks.last().unwrap();

    // 1. Extract Exception code & type
    let mut exception_code = String::new();
    let mut exception_name = String::new();
    let mut thread_name = String::new();
    for line in last_block.lines().take(25) {
        if line.contains("Unhandled Top-Level Exception") || line.contains("c0000005") {
            exception_code = "0xC0000005 (EXCEPTION_ACCESS_VIOLATION)".to_string();
        }
        if line.contains("<<") && line.contains(">>") {
            exception_name = line.replace("-----------------------------------------------------------", "").trim().to_string();
        }
        if line.contains("Thread") && line.contains("Name") {
            if let Some(pos) = line.find(':') {
                thread_name = line[pos + 1..].trim().to_string();
            }
        }
    }

    // 2. Extract RIP Addr
    let mut rip_rva: Option<u32> = None;
    for line in last_block.lines() {
        if line.contains("RIP Addr.:") && line.contains("Yakuza0.exe+") {
            if let Some(pos) = line.find("Yakuza0.exe+") {
                let sub = &line[pos + 12..];
                if let Some(h_pos) = sub.find('h') {
                    if let Ok(val) = u32::from_str_radix(&sub[..h_pos].trim(), 16) {
                        rip_rva = Some(val);
                    }
                }
            }
        }
    }

    // 3. Extract Registers
    let mut regs: HashMap<String, u64> = HashMap::new();
    for line in last_block.lines() {
        for r in &["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"] {
            let pat = format!("{}:", r);
            if let Some(idx) = line.find(&pat) {
                let rest = &line[idx + pat.len()..].trim_start();
                let end = rest.find(|c: char| c.is_whitespace()).unwrap_or(rest.len());
                let val_str = rest[..end].replace("0x", "").replace('h', "");
                if let Ok(v) = u64::from_str_radix(&val_str, 16) {
                    regs.insert(r.to_string(), v);
                }
            }
        }
        for sfr in &["Rbp", "Rsi", "Rdi", "Rsp"] {
            let pat = format!("{}=", sfr);
            if let Some(idx) = line.find(&pat) {
                let rest = &line[idx + pat.len()..].trim_start();
                let end = rest.find(|c: char| c.is_whitespace() || c == ',').unwrap_or(rest.len());
                let val_str = rest[..end].replace("0x", "").replace('h', "");
                if let Ok(v) = u64::from_str_radix(&val_str, 16) {
                    regs.insert(sfr.to_lowercase(), v);
                }
            }
        }
    }

    // 4. Extract Call Stack Frames
    let mut call_stack = Vec::new();
    for line in last_block.lines() {
        if line.contains("Yakuza0.exe+") {
            if let Some(pos) = line.find("Yakuza0.exe+") {
                let sub = &line[pos + 12..];
                let end = sub.find(|c: char| !c.is_ascii_hexdigit()).unwrap_or(sub.len());
                if let Ok(frame_rva) = u32::from_str_radix(&sub[..end], 16) {
                    if !call_stack.contains(&frame_rva) {
                        call_stack.push(frame_rva);
                    }
                }
            }
        }
    }

    let rva = match rip_rva {
        Some(r) => r,
        None => {
            println!("[-] Impossible d'extraire l'adresse RIP du bloc de crash.");
            return;
        }
    };

    println!("[*] Exception : {} {}", exception_code, exception_name);
    if !thread_name.is_empty() {
        println!("[*] Thread    : {}", thread_name);
    }
    println!("[*] Crash RIP : Yakuza0.exe+0x{:X}h (Virtual Address: 0x{:X})", rva, 0x140000000u64 + rva as u64);

    // 5. Read instruction bytes directly from Yakuza0.exe
    if exe_path.exists() {
        if let Some(pe) = PeFile::load(exe_path) {
            if let Some(code_bytes) = pe.read_bytes_at_rva(rva, 16) {
                let hex_str: Vec<String> = code_bytes.iter().map(|b| format!("{:02X}", b)).collect();
                println!("[*] Opcodes x86-64 à RIP : {}", hex_str.join(" "));
            }
        }
    }

    // 6. Print resolved call stack
    if !call_stack.is_empty() {
        println!("\n[*] Pile d'Appels Résolue (Game Engine Call Stack) :");
        for (f_idx, frame_rva) in call_stack.iter().enumerate() {
            let symbol = resolve_rva_symbol(*frame_rva);
            println!("  #{:<2} Yakuza0.exe+0x{:06X}h  -> {}", f_idx, frame_rva, symbol);
        }
    }

    println!("\n[*] État des Registres x86-64 :");
    println!("  RAX = 0x{:016X}   RBX = 0x{:016X}", regs.get("rax").unwrap_or(&0), regs.get("rbx").unwrap_or(&0));
    println!("  RCX = 0x{:016X}   RDX = 0x{:016X}", regs.get("rcx").unwrap_or(&0), regs.get("rdx").unwrap_or(&0));
    println!("  RSI = 0x{:016X}   RDI = 0x{:016X}", regs.get("rsi").unwrap_or(&0), regs.get("rdi").unwrap_or(&0));
    println!("  R8  = 0x{:016X}   R9  = 0x{:016X}", regs.get("r8").unwrap_or(&0), regs.get("r9").unwrap_or(&0));
    println!("  R10 = 0x{:016X}   RBP = 0x{:016X}", regs.get("r10").unwrap_or(&0), regs.get("rbp").unwrap_or(&0));
    println!("  R11 = 0x{:016X}   R12 = 0x{:016X}", regs.get("r11").unwrap_or(&0), regs.get("r12").unwrap_or(&0));

    // 7. Automated Diagnosis based on RVA & in-memory catalog
    println!("\n======================================================================");
    println!("  DIAGNOSTIC AUTOMATIQUE & CAUSE RACINE");
    println!("======================================================================");

    let col_idx = *regs.get("rbp").unwrap_or(&0) as usize;
    let row_idx = *regs.get("r10").unwrap_or(&0) as usize;
    let r9_val = *regs.get("r9").unwrap_or(&0);

    if rva == 0x3711db || (rva >= 0x3711a0 && rva <= 0x371330) {
        println!("  💥 FONCTION : CPropertyTable::BuildColumnIndex (0x1403711a0)");
        println!("  Instruction en faute : movsxd rax, DWORD PTR [r9 + 0x30]");
        println!("\n  Explication :");
        println!("  Le moteur boucle sur les colonnes d'une table RGG (0x20070319) pour indexer les lignes.");
        println!("  - Colonne en cours (ebp) : Index {}", col_idx);
        println!("  - Ligne en cours (r10d)  : Ligne {}", row_idx);
        println!("  - Pointeur R9            : 0x{:016X}", r9_val);
        if r9_val & 0x7 != 0 {
            println!("  [!] ALERTE : %r9 = 0x{:X} n'est pas aligné sur 8 octets ! Pointeur désynchronisé.", r9_val);
        }

        // Instant lookup in static precompiled catalog (0.005 ms)
        let candidates = table_catalog::find_candidates_in_catalog(col_idx, row_idx);
        println!("\n[*] Tables candidates correspondantes (col >= {}, rows >= {}) [Catalogue Mémoire] :", col_idx, row_idx);
        if candidates.is_empty() {
            println!("  [-] Aucune table ne correspond exactement à ces critères.");
        } else {
            for c in &candidates {
                let col_name = if col_idx < c.cols.len() { c.cols[col_idx].name } else { "?" };
                let col_type = if col_idx < c.cols.len() { c.cols[col_idx].col_type } else { 0 };
                println!("  🎯 {} -> {} (Total: {} cols, {} lignes) | Col[{}] = '{}' (type {})", 
                    c.par_name, c.file_name, c.num_cols, c.num_rows, col_idx, col_name, col_type);
            }
        }

        println!("\n  👉 SOLUTION IMMÉDIATE :");
        println!("  Utiliser 'tools/rebuild_clean_stay_inplace.py' pour garantir que toutes les tables");
        println!("  sont logées strictement dans leurs gaps sectoriels natifs sans altération des structures de colonnes.");

    } else if rva == 0x37177c {
        println!("  💥 FONCTION : CPropertyTable::ConvertEndianness (0x14037177c)");
        println!("  Instruction en faute : bswap dans la boucle de lecture de chaîne Type 2.");
        println!("\n  Explication :");
        let esi_col = *regs.get("rsi").unwrap_or(&0) as usize;
        println!("  - Colonne Type 2 (esi) : Index {}", esi_col);
        println!("  - Pointeur de lecture  : 0x{:016X}", regs.get("rax").unwrap_or(&0));
        if esi_col >= 1000 {
            println!("  🚨 ALERTE : Colonne > 1000 détectée ! Ce crash est provoqué par un fichier table hors-archive");
            println!("     (ex: minigame/fishing/*.bin_c) compressé indûment en SLLZ au lieu d'être au format brut 0x20070319 !");
            println!("\n  👉 SOLUTION IMMÉDIATE :");
            println!("  Décompresser les tables hors-archive en format brut 0x20070319 avec variantes .bin et .bin_c.");
        } else {
            println!("  Une chaîne de caractères Type 2 n'a pas son terminateur nul '\\x00' ou la longueur a débordé.");
            println!("\n  👉 SOLUTION IMMÉDIATE :");
            println!("  Vérifier les chaînes de caractères modifiées et appliquer un null-padding strict.");
        }

    } else if rva == 0x234b0 {
        println!("  💥 FONCTION : SLLZ Decompressor Underflow (0x1400234b0)");
        println!("  Instruction en faute : lecture asynchrone sectorielle désalignée dans pause.par");
        println!("\n  Explication :");
        println!("  Une texture 2D (ex: 2d_yk_staminan_lite.dds) a été chargée avec un alignement inférieur à 2 048 octets.");
        println!("  Le streaming disque a injecté du bruit sectoriel (0xfe 0xda) dans le décompresseur SLLZ.");
        println!("\n  👉 SOLUTION IMMÉDIATE :");
        println!("  Recompiler pause.par avec un alignement sectoriel strict de 2 048 octets pour chaque fichier.");

    } else if rva == 0x234b7 {
        println!("  💥 FONCTION : Menu Boutique Pharmacie (Kotobuki / Daikoku)");
        println!("  Tables annexes Pocket Circuit manquantes dans shop0013.bin / shop0029.bin.");
        println!("  👉 SOLUTION : Reconstruire avec 'tools/rebuild_all_shops_clean.py'.");

    } else if rva == 0x6ea328 {
        println!("  💥 FONCTION : MSG Script Bytecode Reader (0x1406ea328)");
        println!("  Instruction en faute : mov ecx, [r9 - 0x8]");
        println!("\n  Explication :");
        println!("  Un script .msg a été lu au-delà de la fin de fichier. Symptôme direct d'un 'wdr.par' tronqué.");
        println!("  👉 SOLUTION : Vérifier que wdr.par fait au moins 7.3 Mo et 241 fichiers.");

    } else if rva == 0xa4526 {
        println!("  💥 FONCTION : Stage Streaming Fixed Offset Mismatch (0x1400a4526)");
        println!("  'response_wanderer.bin_c' a été déplacé de son offset natif 0x9a000 dans stay.par.");
        println!("  👉 SOLUTION : Reconstruire stay.par en mode in-place (offset 0x9a000 strict).");

    } else if rva == 0x371324 {
        println!("  💥 FONCTION : CPropertyTable::GetString (Chaîne vide / Retour NULL)");
        println!("  Instruction en faute : lecture d'un pointeur de chaîne NULL (0x0).");
        println!("\n  Explication :");
        println!("  Une ligne obligatoire dans une table de quête ou d'item a été laissée vide ('') au lieu d'avoir du texte.");
        println!("  - Ligne interrogée : ligne {} (r10d)", row_idx);
        println!("\n  👉 SOLUTION IMMÉDIATE :");
        println!("  Remplir la chaîne manquante dans la table (ex: item.bin_c ou explanation_sub_story.bin_c).");

    } else if rva == 0x396783 {
        println!("  💥 FONCTION : TypewriterEffect / Cabine Téléphonique");
        println!("  Instruction en faute : boucle de décompte de caractères de dialogue.");
        println!("\n  Explication :");
        println!("  La réplique de la cabine téléphonique contient des caractères multi-octets UTF-8 ou n'a pas pile 58 caractères ASCII.");
        println!("  Le moteur attend indéfiniment la fin de l'effet machine à écrire et ne déclenche jamais le menu de sauvegarde.");
        println!("\n  👉 SOLUTION IMMÉDIATE :");
        println!("  Remplacer par 'Sauvegardez et utilisez le coffre depuis une\\r\\ncabine.     ' (pile 58 caractères ASCII).");

    } else if rva == 0x30ed {
        println!("  💥 FONCTION : msvcrt!vsnprintf (Format String Mismatch)");
        println!("  Instruction en faute : spécificateur %s recevant un entier dans une chaîne de format.");
        println!("\n  Explication :");
        println!("  Une chaîne de traduction utilise '%s' au lieu de '%d' pour un montant, niveau ou prix.");
        println!("\n  👉 SOLUTION IMMÉDIATE :");
        println!("  Remplacer '%s' par '%d' dans le dictionnaire de traduction concerné.");

    } else {
        println!("  Signature RVA personnalisée : Yakuza0.exe+0x{:X}h", rva);
        println!("  Consultez docs/DEBUG_KNOWLEDGE_BASE.md pour cette signature.");
    }

    let elapsed = start.elapsed();
    println!("\n----------------------------------------------------------------------");
    println!("  Analyse ultra-rapide terminée en {:.2?}", elapsed);
    println!("======================================================================\n");
}

// ============================================================================
// 8. Standardized Toolbox Functions (Diff, Dump, Inspect, Cell, Scan, Extract)
// ============================================================================
fn extract_par_entry(par_bytes: &[u8], target_name: &str) -> Option<(u32, Vec<u8>)> {
    let entries = parse_par(par_bytes)?;
    for e in entries {
        if e.name.eq_ignore_ascii_case(target_name) {
            let start = e.offset as usize;
            let end = start + e.comp_size as usize;
            if end <= par_bytes.len() {
                let slice = &par_bytes[start..end];
                let is_sllz = (e.flags & 0x80000000) != 0 || (slice.len() >= 4 && &slice[0..4] == b"SLLZ");
                let data = if is_sllz {
                    decompress_sllz(slice)
                } else {
                    slice.to_vec()
                };
                return Some((e.flags, data));
            }
        }
    }
    None
}

fn run_diff_pars(par1_path: &Path, par2_path: &Path) {
    let start = Instant::now();
    println!("======================================================================");
    println!("  RGG PAR DIFF ENGINE (RUST) — Yakuza 0 GOG FR");
    println!("  Archive 1 (Orig) : {}", par1_path.display());
    println!("  Archive 2 (Mod)  : {}", par2_path.display());
    println!("======================================================================\n");

    let b1 = match fs::read(par1_path) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture {}: {}", par1_path.display(), e); return; }
    };
    let b2 = match fs::read(par2_path) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture {}: {}", par2_path.display(), e); return; }
    };

    let entries1 = match parse_par(&b1) {
        Some(e) => e,
        None => { eprintln!("[-] Invalide PARC: {}", par1_path.display()); return; }
    };
    let entries2 = match parse_par(&b2) {
        Some(e) => e,
        None => { eprintln!("[-] Invalide PARC: {}", par2_path.display()); return; }
    };

    let map1: HashMap<String, ParEntry> = entries1.into_iter().map(|e| (e.name.clone(), e)).collect();
    let map2: HashMap<String, ParEntry> = entries2.into_iter().map(|e| (e.name.clone(), e)).collect();

    let mut diff_count = 0;
    let mut missing_count = 0;
    let mut added_count = 0;

    println!("{:<32} {:<10} {:<10} {:<12} {:<12} {:<10}", "Fichier", "Taille 1", "Taille 2", "Flags 1", "Flags 2", "Statut");
    println!("{:-<95}", "");

    let mut sorted_names1: Vec<&String> = map1.keys().collect();
    sorted_names1.sort();

    for name in sorted_names1 {
        let e1 = &map1[name];
        if let Some(e2) = map2.get(name) {
            let start1 = e1.offset as usize;
            let end1 = start1 + e1.comp_size as usize;
            let start2 = e2.offset as usize;
            let end2 = start2 + e2.comp_size as usize;
            let s1 = if end1 <= b1.len() { &b1[start1..end1] } else { &[] };
            let s2 = if end2 <= b2.len() { &b2[start2..end2] } else { &[] };

            let dec1 = if (e1.flags & 0x80000000) != 0 || (s1.len() >= 4 && &s1[..4] == b"SLLZ") { decompress_sllz(s1) } else { s1.to_vec() };
            let dec2 = if (e2.flags & 0x80000000) != 0 || (s2.len() >= 4 && &s2[..4] == b"SLLZ") { decompress_sllz(s2) } else { s2.to_vec() };

            if dec1 != dec2 || e1.flags != e2.flags {
                diff_count += 1;
                println!("{:<32} {:<10} {:<10} 0x{:08X} 0x{:08X} MODIFIÉ (diff: {:+})",
                    name, dec1.len(), dec2.len(), e1.flags, e2.flags, dec2.len() as isize - dec1.len() as isize);
            }
        } else {
            missing_count += 1;
            println!("{:<32} {:<10} {:<10} 0x{:08X} -          SUPPRIMÉ", name, e1.uncomp_size, "-", e1.flags);
        }
    }

    let mut sorted_names2: Vec<&String> = map2.keys().collect();
    sorted_names2.sort();
    for name in sorted_names2 {
        if !map1.contains_key(name) {
            let e2 = &map2[name];
            added_count += 1;
            println!("{:<32} -          {:<10} -          0x{:08X} AJOUTÉ", name, e2.uncomp_size, e2.flags);
        }
    }

    println!("\n----------------------------------------------------------------------");
    println!("  Total fichiers: Archive 1 = {}, Archive 2 = {}", map1.len(), map2.len());
    println!("  Différences constatées : {} modifiés, {} supprimés, {} ajoutés", diff_count, missing_count, added_count);
    println!("  Temps d'exécution : {:.2?}", start.elapsed());
    println!("======================================================================\n");
}

fn run_dump_par(par_path: &Path, filter: Option<&str>) {
    let start = Instant::now();
    println!("======================================================================");
    println!("  RGG PAR DUMP ENGINE (RUST) — Yakuza 0 GOG FR");
    println!("  Archive : {}", par_path.display());
    println!("======================================================================\n");

    let bytes = match fs::read(par_path) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture {}: {}", par_path.display(), e); return; }
    };
    let entries = match parse_par(&bytes) {
        Some(e) => e,
        None => { eprintln!("[-] Invalide PARC: {}", par_path.display()); return; }
    };

    println!("{:<4} {:<34} {:<10} {:<8} {:<8} {:<11} {:<8}",
        "#", "Nom du fichier", "Offset", "Comp Sz", "Uncomp", "Flags", "Gap Disp.");
    println!("{:-<95}", "");

    let filter_lower = filter.map(|f| f.to_lowercase());
    let mut shown = 0;

    for (idx, e) in entries.iter().enumerate() {
        if let Some(ref flt) = filter_lower {
            if !e.name.to_lowercase().contains(flt) {
                continue;
            }
        }
        shown += 1;
        println!("{:<4} {:<34} 0x{:06X}   {:<8} {:<8} 0x{:08X} {:<8}",
            idx, e.name, e.offset, e.comp_size, e.uncomp_size, e.flags, e.available_gap);
    }

    println!("\n----------------------------------------------------------------------");
    println!("  Fichiers affichés : {} / {}", shown, entries.len());
    println!("  Taille totale archive : {} octets", bytes.len());
    println!("  Temps d'exécution : {:.2?}", start.elapsed());
    println!("======================================================================\n");
}

fn run_inspect_table(par_or_file: &Path, table_name: Option<&str>) {
    let start = Instant::now();
    println!("======================================================================");
    println!("  RGG TABLE INSPECTOR (RUST) — Yakuza 0 GOG FR");
    println!("  Source : {}", par_or_file.display());
    if let Some(tn) = table_name {
        println!("  Table  : {}", tn);
    }
    println!("======================================================================\n");

    let bytes = match fs::read(par_or_file) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture {}: {}", par_or_file.display(), e); return; }
    };

    let table_bytes = if let Some(tn) = table_name {
        match extract_par_entry(&bytes, tn) {
            Some((_, d)) => d,
            None => { eprintln!("[-] Table '{}' introuvable dans {}", tn, par_or_file.display()); return; }
        }
    } else if bytes.len() >= 4 && &bytes[0..4] == b"SLLZ" {
        decompress_sllz(&bytes)
    } else {
        bytes
    };

    let table = match parse_rgg_table(&table_bytes) {
        Some(t) => t,
        None => { eprintln!("[-] Non-conforme RGG Property Table (Magic attendu: 0x20070319)"); return; }
    };

    let endian_str = if table.is_big_endian { "Big-Endian (PS3/Switch/WiiU)" } else { "Little-Endian (PC x86-64)" };
    println!("  Format RGG    : 0x20070319 [{}]", endian_str);
    println!("  Colonnes      : {}", table.num_cols);
    println!("  Lignes        : {}", table.num_rows);
    println!("  Taille Totale : {} octets\n", table.data.len());

    println!("{:<4} {:<28} {:<13} {:<8} {:<8} {:<10}",
        "#", "Nom Colonne", "Type", "Count", "Size", "Data Start");
    println!("{:-<85}", "");

    let mut expected_payload = 16 + table.num_cols * 64;
    for (i, c) in table.cols.iter().enumerate() {
        let type_desc = match c.col_type {
            0 => "0 (DenseStr)",
            1 => "1 (EnumDict)",
            2 => "2 (SparseStr)",
            3 => "3 (String)",
            4 => "4 (DictStr)",
            5 => "5 (Sparse16)",
            6 => "6 (Int32)",
            7 => "7 (Int32Term)",
            8 => "8 (StrDirect)",
            9 => "9 (Flag/Int)",
            10 => "10 (UInt32)",
            _ => "Autre",
        };
        println!("{:<4} {:<28} {:<13} {:<8} {:<8} 0x{:06X}",
            i, c.name, type_desc, c.count, c.size, c.data_start);
        expected_payload += c.size as usize;
    }

    println!("\n----------------------------------------------------------------------");
    if expected_payload == table.data.len() {
        println!("  [AUDIT GABARIT] ✅ PARFAIT : Somme colonnes ({}) == Taille fichier ({})", expected_payload, table.data.len());
    } else {
        println!("  [AUDIT GABARIT] ⚠️ ANOMALIE : Somme colonnes ({}) != Taille fichier ({}) [Delta: {:+}]",
            expected_payload, table.data.len(), table.data.len() as isize - expected_payload as isize);
    }
    println!("  Temps d'exécution : {:.2?}", start.elapsed());
    println!("======================================================================\n");
}

fn run_inspect_cell(par_or_file: &Path, table_name: Option<&str>, col_idx: usize, row_idx: usize) {
    let start = Instant::now();
    let bytes = match fs::read(par_or_file) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture: {}", e); return; }
    };
    let table_bytes = if let Some(tn) = table_name {
        match extract_par_entry(&bytes, tn) {
            Some((_, d)) => d,
            None => { eprintln!("[-] Table '{}' introuvable", tn); return; }
        }
    } else if bytes.len() >= 4 && &bytes[0..4] == b"SLLZ" {
        decompress_sllz(&bytes)
    } else {
        bytes
    };

    let table = match parse_rgg_table(&table_bytes) {
        Some(t) => t,
        None => { eprintln!("[-] Non-conforme RGG Property Table"); return; }
    };

    if col_idx >= table.num_cols {
        eprintln!("[-] Index colonne hors limites ({} >= {})", col_idx, table.num_cols);
        return;
    }
    if row_idx >= table.num_rows {
        eprintln!("[-] Index ligne hors limites ({} >= {})", row_idx, table.num_rows);
        return;
    }

    let col = &table.cols[col_idx];
    let data = &table.data;
    let d_start = col.data_start;
    let d_end = d_start + col.size as usize;
    let col_slice = if d_end <= data.len() { &data[d_start..d_end] } else { &[] };

    println!("======================================================================");
    println!("  RGG CELL INSPECTOR — Yakuza 0 GOG FR");
    println!("  Table   : {}", table_name.unwrap_or(par_or_file.to_str().unwrap_or("")));
    println!("  Colonne : {} ('{}', Type {})", col_idx, col.name, col.col_type);
    println!("  Ligne   : {}", row_idx);
    println!("======================================================================\n");

    match col.col_type {
        0 | 3 | 8 => {
            let mut nulls_seen = 0;
            let mut s_start = 0;
            let mut found = false;
            for (idx, &b) in col_slice.iter().enumerate() {
                if nulls_seen == row_idx && !found {
                    s_start = idx;
                    found = true;
                }
                if b == 0 {
                    if nulls_seen == row_idx {
                        let val = String::from_utf8_lossy(&col_slice[s_start..idx]);
                        println!("  VALEUR STRING : \"{}\"", val);
                        println!("  Octets Hex    : {:02X?}", &col_slice[s_start..idx]);
                        break;
                    }
                    nulls_seen += 1;
                }
            }
        }
        1 | 4 => {
            let mut nulls = 0;
            let mut dict_end = 0;
            let mut dict = Vec::new();
            let mut cur_s = 0;
            for (i, &b) in col_slice.iter().enumerate() {
                if b == 0 {
                    dict.push(String::from_utf8_lossy(&col_slice[cur_s..i]).to_string());
                    cur_s = i + 1;
                    nulls += 1;
                    if nulls == col.count as usize {
                        dict_end = cur_s;
                        break;
                    }
                }
            }
            if dict_end + row_idx < col_slice.len() {
                let dict_idx = col_slice[dict_end + row_idx] as usize;
                let val_str = dict.get(dict_idx).cloned().unwrap_or_else(|| "<INDEX_HORS_DICT>".to_string());
                println!("  INDEX DICT    : {} (octet à offset {})", dict_idx, dict_end + row_idx);
                println!("  VALEUR STRING : \"{}\"", val_str);
            } else {
                println!("  [ERREUR] Table de lignes tronquée : offset {} >= taille {}", dict_end + row_idx, col_slice.len());
            }
        }
        2 | 5 => {
            let mut p = 0;
            let mut matched = false;
            while p + 2 < col_slice.len() {
                let r = if table.is_big_endian {
                    u16::from_be_bytes([col_slice[p], col_slice[p + 1]]) as usize
                } else {
                    u16::from_le_bytes([col_slice[p], col_slice[p + 1]]) as usize
                };
                let s_pos = p + 2;
                let mut end = s_pos;
                while end < col_slice.len() && col_slice[end] != 0 {
                    end += 1;
                }
                if r == row_idx {
                    let val = String::from_utf8_lossy(&col_slice[s_pos..end]);
                    println!("  VALEUR SPARSE : \"{}\" (row={})", val, r);
                    matched = true;
                    break;
                }
                p = end + 1;
            }
            if !matched {
                println!("  VALEUR SPARSE : (Non définie / Vide pour la ligne {})", row_idx);
            }
        }
        6 | 7 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 => {
            let off = row_idx * 4;
            if off + 4 <= col_slice.len() {
                let val = if table.is_big_endian {
                    u32::from_be_bytes([col_slice[off], col_slice[off+1], col_slice[off+2], col_slice[off+3]])
                } else {
                    u32::from_le_bytes([col_slice[off], col_slice[off+1], col_slice[off+2], col_slice[off+3]])
                };
                println!("  VALEUR INT32  : {} (0x{:08X})", val, val);
            } else {
                println!("  [ERREUR] Offset integer {} hors limites", off);
            }
        }
        _ => {
            println!("  Type de colonne {} non géré pour affichage unitaire", col.col_type);
        }
    }
    println!("\n  Résolu en {:.2?}", start.elapsed());
    println!("======================================================================\n");
}

fn run_audit_inplace(par_orig_path: &Path, par_mod_path: &Path) {
    let start = Instant::now();
    println!("======================================================================");
    println!("  RGG IN-PLACE AUDITOR (RÈGLE D'OR 3) — Yakuza 0 GOG FR");
    println!("  Pristine Original : {}", par_orig_path.display());
    println!("  Modified Patch    : {}", par_mod_path.display());
    println!("======================================================================\n");

    let b_orig = match fs::read(par_orig_path) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture original: {}", e); return; }
    };
    let b_mod = match fs::read(par_mod_path) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture mod: {}", e); return; }
    };

    let entries_orig = match parse_par(&b_orig) {
        Some(e) => e,
        None => { eprintln!("[-] Original n'est pas un PARC valide"); return; }
    };
    let entries_mod = match parse_par(&b_mod) {
        Some(e) => e,
        None => { eprintln!("[-] Mod n'est pas un PARC valide"); return; }
    };

    let mut issues = 0;

    if b_orig.len() != b_mod.len() {
        println!("  [FAIL] Longueur d'archive modifiée : {} != {} (diff={:+})",
            b_mod.len(), b_orig.len(), b_mod.len() as isize - b_orig.len() as isize);
        issues += 1;
    } else {
        println!("  [PASS] Longueur d'archive bit-exacte : {} octets", b_orig.len());
    }

    let map_mod: HashMap<String, ParEntry> = entries_mod.into_iter().map(|e| (e.name.clone(), e)).collect();

    let mut modified_files = 0;
    for e_orig in &entries_orig {
        if let Some(e_mod) = map_mod.get(&e_orig.name) {
            if e_orig.offset != e_mod.offset {
                println!("  [FAIL] DRIFT D'OFFSET SUR {} : 0x{:06X} -> 0x{:06X}", e_orig.name, e_orig.offset, e_mod.offset);
                issues += 1;
            }
            if e_mod.comp_size > e_orig.available_gap {
                println!("  [FAIL] DÉBORDEMENT DE SECTEUR SUR {} : taille {} > gap {}", e_orig.name, e_mod.comp_size, e_orig.available_gap);
                issues += 1;
            }
            if e_orig.comp_size != e_mod.comp_size || e_orig.flags != e_mod.flags {
                modified_files += 1;
            }
        } else {
            println!("  [FAIL] Fichier original manquant dans mod : {}", e_orig.name);
            issues += 1;
        }
    }

    println!("----------------------------------------------------------------------");
    if issues == 0 {
        println!("  [SUCCÈS TOTAL] 100% CONFORME RÈGLE D'OR 3 (IN-PLACE PUR) !");
        println!("  - 0 drift d'offset sectoriel sur les {} fichiers.", entries_orig.len());
        println!("  - {} fichiers modifiés, tous strictement contenus dans leurs gaps sectoriels.", modified_files);
    } else {
        println!("  [ÉCHEC] {} non-conformités détectées !", issues);
    }
    println!("  Temps d'audit : {:.2?}", start.elapsed());
    println!("======================================================================\n");
}

fn run_scan_candidates(data_dir: &Path, min_cols: usize, min_rows: usize) {
    let start = Instant::now();
    println!("======================================================================");
    println!("  RGG CANDIDATE TABLE SCANNER (RUST) — Yakuza 0 GOG FR");
    println!("  Cible : {}", data_dir.display());
    println!("  Critères : col >= {}, rows >= {}", min_cols, min_rows);
    println!("======================================================================\n");

    let mut pars = Vec::new();
    collect_par_files(data_dir, &mut pars);
    let mut matches = 0;

    println!("{:<32} {:<28} {:<6} {:<8} {:<20}", "Archive PAR", "Table RGG", "Cols", "Rows", format!("Col[{}] Info", min_cols));
    println!("{:-<95}", "");

    for par in &pars {
        let bytes = match fs::read(par) {
            Ok(b) => b,
            Err(_) => continue,
        };
        let entries = match parse_par(&bytes) {
            Some(e) => e,
            None => continue,
        };

        for e in entries {
            if !(e.name.ends_with(".bin_c") || e.name.ends_with(".bin")) {
                continue;
            }
            let s_off = e.offset as usize;
            let e_off = s_off + e.comp_size as usize;
            if e_off > bytes.len() { continue; }
            let slice = &bytes[s_off..e_off];
            let data = if (e.flags & 0x80000000) != 0 || (slice.len() >= 4 && &slice[0..4] == b"SLLZ") {
                decompress_sllz(slice)
            } else {
                slice.to_vec()
            };
            if let Some(table) = parse_rgg_table(&data) {
                if table.num_cols >= min_cols && table.num_rows >= min_rows {
                    matches += 1;
                    let par_disp = par.file_name().unwrap_or_default().to_string_lossy();
                    let col_info = if min_cols < table.cols.len() {
                        let c = &table.cols[min_cols];
                        format!("'{}' (type {})", c.name, c.col_type)
                    } else {
                        "N/A".to_string()
                    };
                    println!("{:<32} {:<28} {:<6} {:<8} {:<20}",
                        par_disp, e.name, table.num_cols, table.num_rows, col_info);
                }
            }
        }
    }

    println!("\n----------------------------------------------------------------------");
    println!("  Total tables correspondantes : {}", matches);
    println!("  Temps de scan : {:.2?}", start.elapsed());
    println!("======================================================================\n");
}

fn run_extract_file(par_path: &Path, file_name: &str, dest_path: Option<&Path>) {
    let start = Instant::now();
    let bytes = match fs::read(par_path) {
        Ok(b) => b,
        Err(e) => { eprintln!("[-] Erreur lecture {}: {}", par_path.display(), e); return; }
    };
    match extract_par_entry(&bytes, file_name) {
        Some((flags, data)) => {
            let out_p = if let Some(dp) = dest_path {
                dp.to_path_buf()
            } else {
                PathBuf::from(file_name)
            };
            if let Err(e) = fs::write(&out_p, &data) {
                eprintln!("[-] Erreur écriture {}: {}", out_p.display(), e);
                return;
            }
            let is_sllz = (flags & 0x80000000) != 0;
            println!("[+] Extrait '{}' -> '{}' ({} octets{}, en {:.2?})",
                file_name, out_p.display(), data.len(), if is_sllz { " décompressés" } else { "" }, start.elapsed());
        }
        None => {
            eprintln!("[-] Fichier '{}' introuvable dans {}", file_name, par_path.display());
        }
    }
}

// ============================================================================
// 9. CLI Main Entry Point
// ============================================================================
fn main() {
    let args: Vec<String> = env::args().collect();
    let default_mode = String::from("preflight");
    let mode = args.get(1).unwrap_or(&default_mode).as_str();

    match mode {
        "preflight" | "check" => {
            let data_dir = if args.len() > 2 {
                PathBuf::from(&args[2])
            } else {
                PathBuf::from("release_gog/data")
            };
            run_preflight(&data_dir);
        }
        "analyze" | "crash" => {
            let log_p = if args.len() > 2 {
                PathBuf::from(&args[2])
            } else {
                PathBuf::from("logs/crash.log")
            };
            let data_dir = if args.len() > 3 {
                PathBuf::from(&args[3])
            } else {
                PathBuf::from("release_gog/data")
            };
            let exe_p = if args.len() > 4 {
                PathBuf::from(&args[4])
            } else {
                PathBuf::from("Yakuza0.exe")
            };
            run_analyze(&log_p, &data_dir, &exe_p);
        }
        "diff-pars" | "diff" => {
            if args.len() < 4 {
                eprintln!("Usage: rgg_preflight diff-pars <archive1.par> <archive2.par>");
                return;
            }
            run_diff_pars(Path::new(&args[2]), Path::new(&args[3]));
        }
        "dump-par" | "dump" | "list" => {
            if args.len() < 3 {
                eprintln!("Usage: rgg_preflight dump-par <archive.par> [filtre]");
                return;
            }
            let filter = args.get(3).map(|s| s.as_str());
            run_dump_par(Path::new(&args[2]), filter);
        }
        "inspect-table" | "table" => {
            if args.len() < 3 {
                eprintln!("Usage: rgg_preflight inspect-table <archive.par|table.bin_c> [table_name]");
                return;
            }
            let table_name = args.get(3).map(|s| s.as_str());
            run_inspect_table(Path::new(&args[2]), table_name);
        }
        "inspect-cell" | "cell" => {
            if args.len() < 5 {
                eprintln!("Usage: rgg_preflight inspect-cell <archive.par> <table_name> <col> <row>");
                eprintln!("   ou: rgg_preflight inspect-cell <table.bin_c> <col> <row>");
                return;
            }
            if args.len() >= 6 {
                let col = args[4].parse::<usize>().unwrap_or(0);
                let row = args[5].parse::<usize>().unwrap_or(0);
                run_inspect_cell(Path::new(&args[2]), Some(&args[3]), col, row);
            } else {
                let col = args[3].parse::<usize>().unwrap_or(0);
                let row = args[4].parse::<usize>().unwrap_or(0);
                run_inspect_cell(Path::new(&args[2]), None, col, row);
            }
        }
        "audit-inplace" | "inplace" => {
            if args.len() < 4 {
                eprintln!("Usage: rgg_preflight audit-inplace <par_original> <par_mod>");
                return;
            }
            run_audit_inplace(Path::new(&args[2]), Path::new(&args[3]));
        }
        "scan-candidates" | "scan" => {
            let data_dir = if args.len() > 2 {
                PathBuf::from(&args[2])
            } else {
                PathBuf::from("release_gog/data")
            };
            let min_cols = if args.len() > 3 { args[3].parse::<usize>().unwrap_or(7) } else { 7 };
            let min_rows = if args.len() > 4 { args[4].parse::<usize>().unwrap_or(400) } else { 400 };
            run_scan_candidates(&data_dir, min_cols, min_rows);
        }
        "extract-file" | "extract" => {
            if args.len() < 4 {
                eprintln!("Usage: rgg_preflight extract-file <archive.par> <nom_fichier> [chemin_destination]");
                return;
            }
            let dest = args.get(4).map(|s| Path::new(s));
            run_extract_file(Path::new(&args[2]), &args[3], dest);
        }
        "watch" => {
            let log_p = if args.len() > 2 {
                PathBuf::from(&args[2])
            } else {
                PathBuf::from("logs/crash.log")
            };
            let actual_log = resolve_log_path(&log_p);
            let data_dir = if args.len() > 3 {
                PathBuf::from(&args[3])
            } else {
                PathBuf::from("release_gog/data")
            };
            let exe_p = if args.len() > 4 {
                PathBuf::from(&args[4])
            } else {
                PathBuf::from("Yakuza0.exe")
            };
            println!("======================================================================");
            println!("  RGG LIVE CRASH SENTRY (RUST ULTRA-PERFORMANCE) — Yakuza 0 GOG FR    ");
            println!("  Surveillance en direct : {}", actual_log.display());
            println!("  Prêt à diagnostiquer tout crash en < 1 milliseconde.");
            println!("  (Appuyez sur Ctrl+C pour quitter)");
            println!("======================================================================\n");
            let mut last_mtime = fs::metadata(&actual_log).and_then(|m| m.modified()).ok();
            loop {
                thread::sleep(Duration::from_millis(300));
                if let Ok(cur_meta) = fs::metadata(&actual_log) {
                    if let Ok(cur_mtime) = cur_meta.modified() {
                        if Some(cur_mtime) != last_mtime {
                            last_mtime = Some(cur_mtime);
                            println!("\n[!] NOUVEAU CRASH DÉTECTÉ DANS LE LOG !");
                            run_analyze(&actual_log, &data_dir, &exe_p);
                        }
                    }
                }
            }
        }
        _ => {
            println!("======================================================================");
            println!("  RGG TOOLBOX (RUST ULTRA-PERFORMANCE) — Yakuza 0 GOG FR");
            println!("======================================================================\n");
            println!("Commandes de Diagnostic & Audit :");
            println!("  preflight [data_dir]                 Audit multi-thread de toutes les 131 archives PAR");
            println!("  crash [log_path] [data_dir] [exe]    Diagnostic instantané (< 1ms) avec pile d'appels");
            println!("  watch [log_path] [data_dir] [exe]    Surveillance en direct du log pendant le jeu");
            println!("  audit-inplace <par_orig> <par_mod>   Valide l'alignement in-place (0 drift sectoriel)");
            println!("  scan-candidates [dir] [cols] [rows]  Cherche les tables candidates (col/row match)\n");
            println!("Commandes d'Inspection & Extraction :");
            println!("  diff-pars <par1> <par2>              Compare 2 archives PAR fichier par fichier");
            println!("  dump-par <par> [filtre]              Affiche les fichiers, offsets hex, gaps et flags");
            println!("  inspect-table <par|file> [table]     Décortique header, colonnes, types et gabarit");
            println!("  inspect-cell <par> <table> <c> <r>   Lit la valeur de la cellule (col, row)");
            println!("  extract-file <par> <file> [dest]     Extrait un fichier (décompression SLLZ auto)");
        }
    }
}


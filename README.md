# itunesbackup2hashcat

A Python tool to extract cryptographic material from iTunes backup files and generate [hashcat](https://hashcat.net) compatible hashes for backup password recovery.

Inspired by [itunes_backup2hashcat.pl](https://github.com/philsmd/itunes_backup2hashcat) by philsmd.

---

## How it works

iTunes backups encrypt their content using a keybag stored in `Manifest.plist`. This tool parses the keybag's TLV (Tag-Length-Value) binary structure to extract:

- **WPKY** — Wrapped class key (40 bytes), encrypted with the backup password
- **SALT** — PBKDF2-SHA1 salt (20 bytes)
- **ITER** — PBKDF2-SHA1 iteration count
- **DPIC** — PBKDF2-SHA256 iteration count *(iOS 10.2+ only)*
- **DPSL** — PBKDF2-SHA256 salt *(iOS 10.2+ only)*


## Requirements

- Python 3.6+
- No external dependencies (uses stdlib only: `plistlib`, `argparse`, `os`)


## Usage

```bash
python itunesbackup2hascat.py -f <path/to/Manifest.plist>
```

### Example

<img width="1043" height="596" alt="image" src="https://github.com/user-attachments/assets/ef4a9c79-8dbd-40dc-94d7-4096e885b19c" />


## Hash formats

| iOS version | Hashcat mode | Format |
|-------------|-------------|--------|
| iOS < 10.2  | `-m 14700`  | `$itunes_backup$*9*<WPKY>*<ITER>*<SALT>**` |
| iOS 10.2+   | `-m 14800`  | `$itunes_backup$*10*<WPKY>*<ITER>*<SALT>*<DPIC>*<DPSL>` |


## Cracking with hashcat

Save the output hash to a file, then run hashcat:

```bash
# iOS 10.2+ (iOS 10.2 to iOS 18+)
hashcat -m 14800 hash.txt wordlist.txt

# iOS < 10.2
hashcat -m 14700 hash.txt wordlist.txt
```

---

## Legal disclaimer

This tool is intended for **lawful use only**, such as recovering access to your own backup. Do not use it against backups you do not own or are not authorized to access.

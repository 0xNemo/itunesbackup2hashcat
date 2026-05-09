import plistlib, argparse, os

# Define TLV values
type_nb_bytes = 4
length_nb_bytes = 4
hash_format = "$itunes_backup$*10*WPKY*ITER*SALT*DPIC*DPSL"
hash_format_ios_before = "$itunes_backup$*9*WPKY*ITER*SALT**"

keys = {"SALT":None, "ITER":None, "DPIC":None, "DPSL":None, "WPKY":None}

parser = argparse.ArgumentParser(description="iTunes Backup to Hashcat")
parser.add_argument("-f", required=True, help="Path to Manifest.plist")
args = parser.parse_args()

# Method to extract all tlv informations by parsing the blob to build the final hash
def get_tlv_value(blob: bytes, tag: str) -> bytes:
    tag_bytes = tag.encode("ascii")
    idx = blob.find(tag_bytes)
    if idx == -1:
        raise ValueError(f"Tag {tag} not found")
    length = blob[idx+type_nb_bytes:][:length_nb_bytes]
    value = blob[idx+type_nb_bytes+length_nb_bytes:][:int.from_bytes(length)]
    if tag == "ITER" or tag == "DPIC" :
        print("-",tag, int.from_bytes(length), int(value.hex(),16))
        return(int(value.hex(),16))
    else :
        print("-",tag, int.from_bytes(length), value.hex())
        return(value.hex())


if __name__ == '__main__':

    print("\n-- ITUNES 2 HASHCAT --\n")
    # Open plist file as dict
    if not os.path.isfile(args.f):
      print(f"[-] File not found : {args.f}")
      exit(1)

    with open(args.f, "rb") as f:
        try:
            data = plistlib.load(f)
        except:
            print("[-] This file is not a valid plist")
            exit(1)

    # Search for BackupKeyBag in Manifest.plist
    if 'BackupKeyBag' in data :
        BackupKey = data['BackupKeyBag']
        print("[+] Try to find values")
        for i in range(len(keys)):
            tag = list(keys)[i]
            try:
                # Parse the blob to find all keys
                part = get_tlv_value(BackupKey, tag)
                keys[tag] = part
            except:
                print(f"[-] {list(keys)[i]} not found")
                exit()

        # Check if it's iOS < 10.2, iOS 10.2+ or if a necessary key is missing
        if keys["DPIC"] is None and keys["DPSL"] is None:
            print("\n[+] iOS < 10.2  →  hash mode -m 14700")
            for word in keys :
                hash_format = hash_format.replace(word, str(keys[word]))
        elif keys["SALT"] is None or keys["ITER"] is None or keys["WPKY"] is None:
            print("[-] A necessary key was not found. Script exit...")
            exit()
        else:
            print("\n[+] iOS 10.2+  →  hash mode -m 14800")
            for word in keys :
                hash_format = hash_format.replace(word, str(keys[word]))
        
        print(f"[+] Final hash : {hash_format}")

    else :
        print("[-s] It seem that this is not Manifest.plist, BackupKeyBag Not found")

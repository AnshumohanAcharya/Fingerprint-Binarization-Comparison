import argparse
import json
import os
import hashlib

from src.biometric import generate_template
from src.fuzzy_commitment import commit, recover
from src.crypto import encrypt_file, decrypt_file


def enroll(fingerprint_image, input_file, encrypted_output, helper_path):
    """Perform the enrollment process described in the project spec."""
    template = generate_template(fingerprint_image)
    key = os.urandom(16)  # 128‑bit AES key
    helper, key_hash = commit(template, key)

    encrypt_file(input_file, encrypted_output, key)

    record = {
        "helper": helper.hex(),
        "key_hash": key_hash.hex(),
        # we might also record the grid size (implicitly encoded in
        # template length) or other parameters in a real system
    }
    with open(helper_path, "w") as f:
        json.dump(record, f)

    print("Enrollment successful")
    print(f"  helper data written to {helper_path}")
    print(f"  encrypted file: {encrypted_output}")


def verify(fingerprint_image, helper_path, encrypted_file, output_file):
    template = generate_template(fingerprint_image)
    with open(helper_path) as f:
        record = json.load(f)
    helper = bytes.fromhex(record["helper"])
    expected = bytes.fromhex(record["key_hash"])

    key = recover(template, helper)
    if key is None:
        print("Biometric did not match; key recovery failed")
        return
    if hashlib.sha256(key).digest() != expected:
        print("Recovered key hash differs; aborting")
        return

    decrypt_file(encrypted_file, output_file, key)
    print("Decryption successful")
    print(f"  output written to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Secure file encryption demo")
    sub = parser.add_subparsers(dest="command")

    p_enroll = sub.add_parser("enroll", help="bind a key to a fingerprint")
    p_enroll.add_argument("--fingerprint", required=True,
                          help="path to fingerprint image")
    p_enroll.add_argument("--infile", required=True,
                          help="file to encrypt")
    p_enroll.add_argument("--outfile", required=True,
                          help="destination for encrypted file")
    p_enroll.add_argument("--helper", required=True,
                          help="path where helper data will be stored")

    p_verify = sub.add_parser("verify", help="decrypt using a fingerprint")
    p_verify.add_argument("--fingerprint", required=True,
                          help="path to fingerprint image")
    p_verify.add_argument("--helper", required=True,
                          help="helper data produced earlier")
    p_verify.add_argument("--encrypted", required=True,
                          help="encrypted file from enrollment")
    p_verify.add_argument("--out", required=True,
                          help="where to write decrypted output")

    args = parser.parse_args()
    if args.command == "enroll":
        enroll(args.fingerprint, args.infile, args.outfile, args.helper)
    elif args.command == "verify":
        verify(args.fingerprint, args.helper, args.encrypted, args.out)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

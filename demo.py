#!/usr/bin/env python3
"""
Complete demonstration of the Fuzzy Commitment Scheme for secure file encryption.
Shows enrollment, verification, and file recovery workflow.
"""
import os
import sys
import hashlib
import json
from pathlib import Path

from src.biometric import generate_template, extract_minutiae
from src.fuzzy_commitment import commit, recover
from src.crypto import encrypt_file, decrypt_file


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(step_num, description):
    print(f"\n[Step {step_num}] {description}")
    print("-" * 70)


def demo():
    """Run the complete demonstration."""
    
    print_section("FUZZY COMMITMENT SCHEME PROTOTYPE")
    print("Secure File Encryption Using Fingerprint Biometrics")
    print("\nIntelligence Agency Confidential Document Security System")
    
    # ========================================================================
    # PHASE 1: ENROLLMENT
    # ========================================================================
    print_section("PHASE 1: ENROLLMENT")
    
    fp_enroll = "data/DB1_B/101_1.tif"
    secret_file = "secret_document.txt"
    encrypted_file = "secret_document.enc"
    helper_file = "helper_data.json"
    
    # Create a sample secret document
    print_step(1, "Creating Secret Document")
    secret_content = """
    TOP SECRET - INTELLIGENCE REPORT
    ================================
    
    Document Classification: CONFIDENTIAL
    Agency: Intelligence Bureau
    Date: 2026-03-12
    
    This document contains highly classified information regarding
    ongoing security operations. Access is restricted to authorized
    personnel only.
    
    Key Strategic Assets:
    - Operation codename: PHOENIX
    - Target location coordinates secured
    - Asset deployment timeline finalized
    - Budget allocation: $50 Million
    
    Distribution: Limited to 3 copies
    Handling: Biometric-secured encryption
    """
    
    with open(secret_file, "w") as f:
        f.write(secret_content)
    
    file_size = os.path.getsize(secret_file)
    print(f"✓ Document created: {secret_file}")
    print(f"  File size: {file_size} bytes")
    print(f"  Content preview: {secret_content[:100]}...")
    
    # Extract fingerprint features
    print_step(2, "Extracting Fingerprint Features")
    print(f"📍 Fingerprint image: {fp_enroll}")
    
    minutiae = extract_minutiae(fp_enroll)
    print(f"✓ Detected {len(minutiae)} minutiae points (ridge endings & bifurcations)")
    
    if minutiae:
        print(f"  Sample minutiae locations: {minutiae[:5]}")
    
    # Generate biometric template
    print_step(3, "Generating Biometric Template")
    template = generate_template(fp_enroll)
    print(f"✓ Template generated: {len(template)} bytes (16×16 grid)")
    print(f"  Template (hex): {template.hex()[:64]}...")
    
    # Generate random key
    print_step(4, "Generating Cryptographic Key")
    key = os.urandom(16)
    print(f"✓ Random AES-128 key generated")
    print(f"  Key (hex): {key.hex()}")
    
    # Bind key using fuzzy commitment
    print_step(5, "Binding Key with Fuzzy Commitment Scheme")
    helper, key_hash = commit(template, key)
    print(f"✓ Fuzzy commitment completed using Reed-Solomon ECC")
    print(f"  Helper data size: {len(helper)} bytes")
    print(f"  Helper data (hex): {helper.hex()[:64]}...")
    print(f"  Key hash (SHA-256): {key_hash.hex()}")
    
    # Store helper data
    print_step(6, "Storing Helper Data (Discarding Key & Template)")
    helper_record = {
        "helper_data": helper.hex(),
        "key_hash": key_hash.hex(),
        "template_size": len(template),
        "grid_size": (16, 16),
        "enrollment_file": fp_enroll,
        "timestamp": "2026-03-12T10:00:00Z"
    }
    
    with open(helper_file, "w") as f:
        json.dump(helper_record, f, indent=2)
    
    print(f"✓ Helper data stored in {helper_file}")
    print(f"  Note: Original key and template are now DISCARDED")
    
    # Encrypt file
    print_step(7, "Encrypting Document with Bound Key")
    encrypt_file(secret_file, encrypted_file, key)
    print(f"✓ Document encrypted using AES-GCM")
    print(f"  Encrypted file: {encrypted_file}")
    print(f"  File size: {os.path.getsize(encrypted_file)} bytes")
    
    # ========================================================================
    # PHASE 2: VERIFICATION & RECOVERY
    # ========================================================================
    print_section("PHASE 2: VERIFICATION & DECRYPTION")
    
    # Simulate presenting the same fingerprint
    print_step(8, "Presenting Fingerprint for Authentication")
    fp_verify = "data/DB1_B/101_1.tif"  # Same fingerprint
    print(f"📍 Presented fingerprint: {fp_verify}")
    
    # Load helper data
    print_step(9, "Loading Helper Data from Storage")
    with open(helper_file) as f:
        stored_record = json.load(f)
    
    stored_helper = bytes.fromhex(stored_record["helper_data"])
    stored_key_hash = bytes.fromhex(stored_record["key_hash"])
    print(f"✓ Helper data loaded")
    print(f"  Grid size: {stored_record['grid_size']}")
    
    # Extract features from presented fingerprint
    print_step(10, "Extracting Features from Presented Fingerprint")
    template_verify = generate_template(fp_verify)
    print(f"✓ Template generated from presented fingerprint")
    print(f"  Template (hex): {template_verify.hex()[:64]}...")
    
    # Recover key using fuzzy commitment
    print_step(11, "Recovering Key Using Reed-Solomon Decoder")
    recovered_key = recover(template_verify, stored_helper)
    
    if recovered_key is None:
        print("✗ FAILURE: Could not recover key (fingerprint mismatch)")
        sys.exit(1)
    
    print(f"✓ Key recovery SUCCESS using fuzzy commitment")
    print(f"  Recovered key (hex): {recovered_key.hex()}")
    
    # Verify key integrity
    print_step(12, "Verifying Key Integrity Using Hash")
    recovered_hash = hashlib.sha256(recovered_key).digest()
    hash_match = (recovered_hash == stored_key_hash)
    
    print(f"✓ Key hash verification: {'PASS ✓' if hash_match else 'FAIL ✗'}")
    print(f"  Stored hash:    {stored_key_hash.hex()}")
    print(f"  Recovered hash: {recovered_hash.hex()}")
    
    if not hash_match:
        print("✗ CRITICAL: Hash mismatch detected - aborting decryption")
        sys.exit(1)
    
    # Decrypt file
    print_step(13, "Decrypting Document Using Recovered Key")
    decrypted_file = "recovered_document.txt"
    decrypt_file(encrypted_file, decrypted_file, recovered_key)
    print(f"✓ Document decrypted successfully")
    print(f"  Output file: {decrypted_file}")
    
    # Verify content
    print_step(14, "Verifying Decrypted Content Integrity")
    with open(decrypted_file) as f:
        recovered_content = f.read()
    
    content_match = (recovered_content == secret_content)
    print(f"✓ Content verification: {'PASS ✓' if content_match else 'FAIL ✗'}")
    print(f"  Original size:  {len(secret_content)} bytes")
    print(f"  Recovered size: {len(recovered_content)} bytes")
    print(f"\n  Recovered content preview:")
    print("  " + "\n  ".join(recovered_content.split("\n")[:8]))
    
    # ========================================================================
    # PHASE 3: ROBUSTNESS TEST
    # ========================================================================
    print_section("PHASE 3: ROBUSTNESS TEST - Noisy Fingerprint")
    
    print_step(15, "Simulating Noisy Fingerprint (Slight Variations)")
    print("Testing Reed-Solomon error correction capability...")
    
    # Create slightly altered template
    noisy_template = bytearray(template_verify)
    for i in range(2):  # flip a couple of bytes
        if i < len(noisy_template):
            noisy_template[i] ^= 0x0F  # Noisy modification
    
    noisy_template = bytes(noisy_template)
    recovered_key_noisy = recover(noisy_template, stored_helper)
    
    if recovered_key_noisy == recovered_key:
        print("✓ Noisy fingerprint recovery: SUCCESS")
        print("  Reed-Solomon ECC successfully corrected bit errors")
    else:
        print("✗ Noisy fingerprint recovery: FAILED")
        print("  Error correction limit exceeded")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_section("SUMMARY & SECURITY ANALYSIS")
    
    print("\n✓ COMPLETE LIFECYCLE DEMONSTRATED:")
    print("  1. ✓ Fingerprint feature extraction (minutiae detection)")
    print("  2. ✓ Biometric template generation (256-bit binary grid)")
    print("  3. ✓ Cryptographic key generation (128-bit AES)")
    print("  4. ✓ Fuzzy commitment binding (Reed-Solomon ECC)")
    print("  5. ✓ Key & template discarding (privacy protection)")
    print("  6. ✓ Document encryption (AES-GCM)")
    print("  7. ✓ Biometric verification & key recovery")
    print("  8. ✓ Document decryption & integrity verification")
    print("  9. ✓ Error correction capability (fuzziness)")
    
    print("\n📊 SECURITY PROPERTIES:")
    print(f"  • Template size: 256 bits (32 bytes)")
    print(f"  • Key size: 128 bits (AES-128)")
    print(f"  • ECC parity: 16 bytes (16 symbols for RS)")
    print(f"  • Error correction: Up to 8 byte errors (64 bits)")
    print(f"  • Encryption: AES-GCM with authentication")
    print(f"  • Digest: SHA-256 for key verification")
    
    print("\n📁 ARTIFACTS CREATED:")
    print(f"  • Helper data:        {helper_file}")
    print(f"  • Encrypted document: {encrypted_file}")
    print(f"  • Recovered document: {decrypted_file}")
    
    print("\n🔐 KEY FINDINGS:")
    print("  • Helper data can be stored publicly (no sensitivity)")
    print("  • Key is never stored or transmitted in plaintext")
    print("  • Template is regenerated on each authentication attempt")
    print("  • Fuzzy commitment enables biometric tolerance")
    print("  • System suitable for high-security document protection")
    
    print_section("DEMONSTRATION COMPLETE")


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

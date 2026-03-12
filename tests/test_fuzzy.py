import os
import tempfile
import hashlib

from src.biometric import generate_template
from src.fuzzy_commitment import commit, recover


def test_commit_recover():
    # use one of the dataset images
    img = os.path.join("data", "DB1_B", "101_1.tif")
    template = generate_template(img)
    key = os.urandom(16)
    helper, key_hash = commit(template, key)

    # recover using identical template
    rec = recover(template, helper)
    assert rec == key
    assert hashlib.sha256(rec).digest() == key_hash

    # alter the template by flipping a bit
    template2 = bytearray(template)
    template2[0] ^= 0x01
    # recovery may still succeed or fail depending on error budget
    recovered = recover(bytes(template2), helper)
    assert recovered in (key, None)


if __name__ == "__main__":
    test_commit_recover()
    print("fuzzy tests passed")

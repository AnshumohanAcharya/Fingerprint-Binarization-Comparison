import os

from Crypto.Cipher import AES


NONCE_SIZE = 16
TAG_SIZE = 16


def encrypt_file(in_path: str, out_path: str, key: bytes):
    """Encrypt the contents of ``in_path`` with AES‑GCM and write to
    ``out_path``.

    The output format is: nonce (16) | tag (16) | ciphertext.
    """
    cipher = AES.new(key, AES.MODE_GCM)
    with open(in_path, "rb") as f:
        plaintext = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    with open(out_path, "wb") as f:
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)


def decrypt_file(in_path: str, out_path: str, key: bytes):
    """Read ``in_path`` (produced by :func:`encrypt_file`) and decrypt it.

    ``out_path`` is created or overwritten with the recovered plaintext.
    """
    with open(in_path, "rb") as f:
        nonce = f.read(NONCE_SIZE)
        tag = f.read(TAG_SIZE)
        ciphertext = f.read()
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    with open(out_path, "wb") as f:
        f.write(plaintext)

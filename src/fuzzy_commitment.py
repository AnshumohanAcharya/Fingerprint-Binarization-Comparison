import hashlib

import reedsolo


# choose parameters so that the codeword length matches the biometric template
# produced by ``generate_template`` in ``biometric.py`` (default 16x16=256 bits =
# 32 bytes).  We use a 16‑byte message (the symmetric key) and 16 bytes of
# parity.
RS_PARITY = 16


def _get_rs():
    # there is some global state in reedsolo; create a fresh object each time.
    return reedsolo.RSCodec(nsym=RS_PARITY)


def commit(template: bytes, key: bytes):
    """Bind a random key to biometric ``template``.

    ``template`` and the resulting codeword are required to be the same length.
    Returns a tuple ``(helper_data, key_hash)`` where ``helper_data`` is the
    XOR of the codeword with the template and ``key_hash`` is SHA‑256 of the
    original key (used later to verify that the correct key was recovered).
    """
    rs = _get_rs()
    msglen = 255 - RS_PARITY  # reedsolo GF(256) max codeword is 255
    if len(key) > msglen:
        raise ValueError(f"key too long (max {msglen} bytes)")
    codeword = bytes(rs.encode(key))
    if len(codeword) != len(template):
        raise ValueError("template length does not match RS codeword length")
    helper = bytes(a ^ b for a, b in zip(codeword, template))
    key_hash = hashlib.sha256(key).digest()
    return helper, key_hash


def recover(template: bytes, helper: bytes):
    """Attempt to reconstruct the key given a new ``template`` and stored
    ``helper`` data.

    If the biometric is close enough to the original, Reed‑Solomon decoding
    will succeed and the key bytes are returned.  Otherwise ``None`` is
    returned.
    """
    if len(template) != len(helper):
        raise ValueError("template/helper length mismatch")
    codeword = bytes(a ^ b for a, b in zip(helper, template))
    rs = _get_rs()
    try:
        # decode() returns (message, ecc_bytes, errata_positions)
        decoded = rs.decode(codeword)
        key = decoded[0]  # extract just the message portion
        # ``reedsolo`` may return a ``bytearray``; normalise to ``bytes``
        return bytes(key) if isinstance(key, (bytes, bytearray)) else key
    except Exception:
        return None

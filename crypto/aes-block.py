import pyaes
import struct

CIPHERTEXT_CBC1 = bytearray.fromhex( \
    "4ca00ff4c898d61e1edbf1800618fb2828a226d1" + \
    "60dad07883d04e008a7897ee2e4b7465d5290d0c" + \
    "0e6c6822236e1daafb94ffe0c5da05d9476be028" + \
    "ad7c1d81" \
)
KEY_CBC1 = bytearray.fromhex("140b41b22a29beb4061bda66b6747e14")

CIPHERTEXT_CBC2 = bytearray.fromhex( \
    "5b68629feb8606f9a6667670b75b38a5b4832d0f" + \
    "26e1ab7da33249de7d4afc48e713ac646ace36e8" + \
    "72ad5fb8a512428a6e21364b0c374df45503473c" + \
    "5242a253" \
)
KEY_CBC2 = bytearray.fromhex("140b41b22a29beb4061bda66b6747e14")

CIPHERTEXT_CTR1 = bytearray.fromhex( \
    "69dda8455c7dd4254bf353b773304eec0ec77023" \
    "30098ce7f7520d1cbbb20fc388d1b0adb5054dbd" \
    "7370849dbf0b88d393f252e764f1f5f7ad97ef79" \
    "d59ce29f5f51eeca32eabedd9afa9329" \
)
KEY_CTR1 = bytearray.fromhex("36f18357be4dbd77f050515c73fcf9f2")

def xor(alst, blst):
    return bytearray(a ^ b for a, b in zip(alst, blst))

def _bytes_to_string(binary):
    return "".join(chr(b) for b in binary)

def cbs_encrypt(iv, key, msg):
    aes = pyaes.AES(key)
    xor_factor = iv
    out = bytearray()
    for chunk in blockify(msg):
        ciphertext = aes.encrypt(xor(xor_factor, chunk))
        out.extend(ciphertext)
        xor_factor = ciphertext
    return out

def cbs_decrypt(iv, key, msg):
    aes = pyaes.AES(key)
    out = bytearray()
    xor_factor = iv
    for chunk in blockify(msg):
        plaintext = xor(xor_factor, aes.decrypt(chunk))
        out.extend(plaintext)
        xor_factor = chunk
    return out

def ctr_encrypt(iv, key, msg):
    aes = pyaes.AES(key)
    ctr = 0
    out = bytearray()
    for chunk in blockify(msg):
        iv_ctr = iv + bytearray(struct.pack("<Q", ctr))
        print(iv_ctr)
        out.extend(xor(msg, aes.encrypt(iv_ctr)))
        ctr += 1
    return out

def ctr_decrypt(iv, key, msg):
    aes = pyaes.AES(key)
    ctr = 0
    out = bytearray()
    for chunk in blockify(msg):
        iv_ctr = iv[:8] + bytearray(struct.pack("Q", ctr))
        out.extend(xor(msg, aes.decrypt(iv_ctr)))
        ctr += 1
    return out

def extract_iv(raw, use_ctr=False):
    offset = 16
    return raw[:offset], raw[offset:len(raw)]

def blockify(msg):
    n = 16
    for i in range(0, len(msg), n):
        yield msg[i:i + n]

iv, cipher = extract_iv(CIPHERTEXT_CBC1)
decrypted = cbs_decrypt(iv, KEY_CBC1, cipher)
print("CBC1:", decrypted)

iv, cipher = extract_iv(CIPHERTEXT_CBC2)
decrypted = cbs_decrypt(iv, KEY_CBC2, cipher)
print("CBC2:", decrypted)

iv, cipher = extract_iv(CIPHERTEXT_CTR1, use_ctr=True)
decrypted = ctr_decrypt(iv, KEY_CTR1, cipher)
print("CTR1:", decrypted)

aes = pyaes.AESModeOfOperationCTR(KEY_CTR1)
decrypted = aes.decrypt(_bytes_to_string(CIPHERTEXT_CTR1))
print(decrypted)
import os
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def get_hashed_password(password: str) -> bytes:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(password.encode())
    return digest.finalize()


def encrypt(plain_text: str, password: str) -> bytes:
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()

    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(get_hashed_password(password)),
                    modes.CBC(iv))
    encryptor = cipher.encryptor()
    return iv + encryptor.update(padded_data) + encryptor.finalize()


def decrypt(cipher_with_iv: bytes, password: str) -> str:
    iv, cipher = cipher_with_iv[:16], cipher_with_iv[16:]
    decryptor = Cipher(algorithms.AES(get_hashed_password(password)),
                       modes.CBC(iv)).decryptor()

    plain_b4_unpadding = decryptor.update(cipher) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plain_binary = unpadder.update(plain_b4_unpadding) + unpadder.finalize()
    return plain_binary.decode()

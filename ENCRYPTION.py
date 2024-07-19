from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import configparser
import os

# Function to pad the plaintext to be a multiple of 16 bytes (AES block size)
def pad(data):
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length

# Function to unpad the decrypted data
def unpad(data):
    return data[:-data[-1]]

# Function to encrypt an ini file
def encrypt_ini_file(input_file, output_file, aes_key):
    # Read the ini file
    config = configparser.ConfigParser()
    config.read(input_file)

    # Convert the ini data to a bytes object
    ini_data = config.get('section_name', 'key_name').encode()

    # Generate a random 16-byte initialization vector (IV)
    iv = os.urandom(16)

    # Encrypt the plaintext
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_plaintext = encryptor.update(pad(ini_data)) + encryptor.finalize()

    # Write the IV and encrypted data to a file
    with open(output_file, 'wb') as f:
        f.write(iv + padded_plaintext)

    print(f"Encryption successful. Encrypted file saved as {output_file}")

# Function to decrypt an ini file
def decrypt_ini_file(input_file, output_file, aes_key):
    # Read the encrypted file
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()

    # Extract the IV and encrypted data
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]

    # Decrypt the data
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Unpad the decrypted data
    unpadded_data = unpad(decrypted_data)

    # Decode the decrypted bytes to string
    decrypted_text = unpadded_data.decode()

    # Write the decrypted data to a new ini file
    with open(output_file, 'w') as f:
        f.write(decrypted_text)

    print(f"Decryption successful. Decrypted file saved as {output_file}")

if __name__ == "__main__":
    # Replace with your AES key (must be 16, 24, or 32 bytes long for AES-128, AES-192, or AES-256 respectively)
    aes_key = b'ThisIsASecretAESKey'

    # Paths to input and output files
    input_ini_file = 'input.ini'
    encrypted_ini_file = 'encrypted_ini_file.ini'
    decrypted_ini_file = 'decrypted_ini_file.ini'

    # Encrypt the ini file
    encrypt_ini_file(input_ini_file, encrypted_ini_file, aes_key)

    # Decrypt the encrypted ini file
    decrypt_ini_file(encrypted_ini_file, decrypted_ini_file, aes_key)


import argparse
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- Key Generation ---
def generate_rsa_key_pair(private_key_path, public_key_path):
    """Generates RSA private and public key files."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Write private key to file
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write public key to file
    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print(f"RSA key pair generated: {private_key_path} and {public_key_path}")

# --- Encryption ---
def encrypt_file(file_path, public_key_path, output_file_path):
    """Encrypts a file using RSA public key and AES symmetric encryption."""
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    # Generate a random AES key for symmetric encryption
    aes_key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)  # 128-bit IV

    # Encrypt the AES key with RSA public key
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Encrypt the file content with AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(file_path, "rb") as infile, open(output_file_path, "wb") as outfile:
        outfile.write(encrypted_aes_key)  # Write encrypted AES key
        outfile.write(iv)  # Write IV
        while True:
            chunk = infile.read(4096)
            if not chunk:
                break
            outfile.write(encryptor.update(chunk))
        outfile.write(encryptor.finalize())

    print(f"File '{file_path}' encrypted to '{output_file_path}'")

# --- Decryption ---
def decrypt_file(encrypted_file_path, private_key_path, output_file_path):
    """Decrypts a file using RSA private key and AES symmetric decryption."""
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # Assuming no password for the private key
            backend=default_backend()
        )

    with open(encrypted_file_path, "rb") as infile:
        # Read encrypted AES key
        encrypted_aes_key_len = private_key.key_size // 8  # RSA key size in bytes
        encrypted_aes_key = infile.read(encrypted_aes_key_len)

        # Read IV
        iv = infile.read(16)

        # Decrypt the AES key with RSA private key
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the file content with AES
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        with open(output_file_path, "wb") as outfile:
            while True:
                chunk = infile.read(4096)
                if not chunk:
                    break
                outfile.write(decryptor.update(chunk))
            outfile.write(decryptor.finalize())

    print(f"File '{encrypted_file_path}' decrypted to '{output_file_path}'")

# --- Main function and Argument Parsing ---
def main():
    parser = argparse.ArgumentParser(description="RSA File Encryptor/Decryptor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate Key Pair command
    generate_parser = subparsers.add_parser("generate", help="Generate RSA key pair")
    generate_parser.add_argument("--private-key", required=True, help="Path to save the private key (PEM format)")
    generate_parser.add_argument("--public-key", required=True, help="Path to save the public key (PEM format)")

    # Encrypt command
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    encrypt_parser.add_argument("--file", required=True, help="Path to the file to encrypt")
    encrypt_parser.add_argument("--public-key", required=True, help="Path to the public key PEM file")
    encrypt_parser.add_argument("--output", required=True, help="Path for the encrypted output file")

    # Decrypt command
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    decrypt_parser.add_argument("--file", required=True, help="Path to the encrypted file")
    decrypt_parser.add_argument("--private-key", required=True, help="Path to the private key PEM file")
    decrypt_parser.add_argument("--output", required=True, help="Path for the decrypted output file")

    args = parser.parse_args()

    if args.command == "generate":
        generate_rsa_key_pair(args.private_key, args.public_key)
    elif args.command == "encrypt":
        encrypt_file(args.file, args.public_key, args.output)
    elif args.command == "decrypt":
        decrypt_file(args.file, args.private_key, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

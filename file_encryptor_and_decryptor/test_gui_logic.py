
from rsa_gui_cryptor import generate_rsa_key_pair, encrypt_file, decrypt_file
import os

def test_logic():
    print("Testing RSA GUI logic...")
    
    # 1. Generate keys
    success, msg = generate_rsa_key_pair('gui_private.pem', 'gui_public.pem')
    print(msg)
    if not success: return

    # 2. Create test file
    with open('gui_test.txt', 'w') as f:
        f.write('GUI Test Message: RSA Encryption is working!')

    # 3. Encrypt
    success, msg = encrypt_file('gui_test.txt', 'gui_public.pem', 'gui_encrypted.bin')
    print(msg)
    if not success: return

    # 4. Decrypt
    success, msg = decrypt_file('gui_encrypted.bin', 'gui_private.pem', 'gui_decrypted.txt')
    print(msg)
    if not success: return

    # 5. Verify
    with open('gui_decrypted.txt', 'r') as f:
        content = f.read()
        print(f"Decrypted content: {content}")
        if content == 'GUI Test Message: RSA Encryption is working!':
            print("SUCCESS: Logic test passed!")
        else:
            print("FAILURE: Decrypted content does not match.")

if __name__ == "__main__":
    test_logic()

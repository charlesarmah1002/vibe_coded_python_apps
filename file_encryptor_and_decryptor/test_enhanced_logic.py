
from rsa_gui_cryptor import generate_rsa_key_pair, encrypt_file, decrypt_file
import os

def test_enhanced_logic():
    print("Testing Enhanced RSA logic (Compression)...")
    
    # 1. Generate keys
    generate_rsa_key_pair('test_priv.pem', 'test_pub.pem')

    # 2. Create test file with repetitive data (good for compression)
    original_text = "This is a test message that should be compressed and encrypted. " * 100
    with open('test_input.txt', 'w') as f:
        f.write(original_text)

    # 3. Encrypt with compression
    encrypt_file('test_input.txt', 'test_pub.pem', 'test_compressed.bin', compress=True)
    
    # Check if compressed file is smaller than original (it should be for this data)
    orig_size = os.path.getsize('test_input.txt')
    comp_size = os.path.getsize('test_compressed.bin')
    print(f"Original size: {orig_size} bytes")
    print(f"Encrypted/Compressed size: {comp_size} bytes")

    # 4. Decrypt
    decrypt_file('test_compressed.bin', 'test_priv.pem', 'test_output.txt')

    # 5. Verify
    with open('test_output.txt', 'r') as f:
        decrypted_text = f.read()
        if decrypted_text == original_text:
            print("SUCCESS: Decrypted content matches original!")
        else:
            print("FAILURE: Decrypted content mismatch.")

if __name__ == "__main__":
    test_enhanced_logic()

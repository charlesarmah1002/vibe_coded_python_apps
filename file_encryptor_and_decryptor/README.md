# RSA File Cryptor

This project provides a simple way to encrypt and decrypt files using RSA keys. It includes both:

- a graphical desktop application in `rsa_gui_cryptor.py`
- a command-line tool in `rsa_file_cryptor.py`

The app can also optionally compress files and remove metadata from images and PDF files before encryption.

## Features

- Generate RSA 2048-bit public/private key pairs in PEM format
- Encrypt files with RSA + AES
- Decrypt files back to their original contents
- Optional compression before encryption
- Optional metadata removal for common image formats and PDF files
- Works through either a GUI or the command line

## Requirements

- Python 3.9 or newer
- Windows is supported directly; the same code can also run on other operating systems

Install the required Python packages:

```bash
pip install cryptography pillow pikepdf
```

If you want to keep the project isolated, create a virtual environment first:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install cryptography pillow pikepdf
```

## Running the GUI Application

Start the desktop app with:

```bash
python rsa_gui_cryptor.py
```

### How to use the GUI

1. Generate a key pair
   - Enter a path for the private key, such as `private.pem`
   - Enter a path for the public key, such as `public.pem`
   - Click "Generate Keys"

2. Encrypt a file
   - Choose the file you want to protect
   - Choose the public key file
   - Choose an output path for the encrypted file
   - Optionally enable:
     - "Compress File"
     - "Remove Metadata (Images/PDFs)"
   - Click "Encrypt"

3. Decrypt a file
   - Choose the encrypted file
   - Choose the matching private key file
   - Choose an output path for the decrypted file
   - Click "Decrypt"

> Keep your private key safe. The public key can be shared, but the private key is required to decrypt files.

## Running from the Command Line

### Generate a key pair

```bash
python rsa_file_cryptor.py generate --private-key private.pem --public-key public.pem
```

### Encrypt a file

```bash
python rsa_file_cryptor.py encrypt --file secret.txt --public-key public.pem --output secret.bin
```

### Decrypt a file

```bash
python rsa_file_cryptor.py decrypt --file secret.bin --private-key private.pem --output secret.txt
```

## Notes

- The encrypted output is not a standard text file. It is a binary file produced by the program.
- Compression and metadata removal are handled automatically when those options are enabled.
- Metadata removal is mainly useful for image and PDF files, where hidden information may be stored in file headers or document properties.

## Optional Tests

The repository also includes example test scripts:

```bash
python test_gui_logic.py
python test_enhanced_logic.py
python test_metadata_removal.py
```

These can be used to verify the core encryption, compression, and metadata removal behavior.

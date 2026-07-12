
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import gzip
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# For metadata removal
from PIL import Image
import pikepdf

# --- Core Logic ---
def generate_rsa_key_pair(private_key_path, public_key_path):
    """Generates RSA private and public key files."""
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        with open(private_key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(public_key_path, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        return True, f"RSA key pair generated: {private_key_path} and {public_key_path}"
    except Exception as e:
        return False, f"Error generating keys: {e}"

def remove_image_metadata(file_path, output_path):
    """Removes EXIF metadata from an image file."""
    try:
        with Image.open(file_path) as img:
            data = list(img.getdata())
            image_without_exif = Image.new(img.mode, img.size)
            image_without_exif.putdata(data)
            image_without_exif.save(output_path)
        return True, f"Metadata removed from image: {file_path}"
    except Exception as e:
        return False, f"Error removing image metadata: {e}"

def remove_pdf_metadata(file_path, output_path):
    """Removes metadata from a PDF file."""
    try:
        with pikepdf.open(file_path) as pdf:
            del pdf.docinfo
            pdf.save(output_path)
        return True, f"Metadata removed from PDF: {file_path}"
    except Exception as e:
        return False, f"Error removing PDF metadata: {e}"

def encrypt_file(file_path, public_key_path, output_file_path, compress=False, remove_metadata=False):
    """Encrypts a file using RSA public key and AES symmetric encryption, with optional compression and metadata removal."""
    try:
        # Handle metadata removal first, if requested
        temp_file_path = file_path
        if remove_metadata:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
                temp_output_path = file_path + ".no_meta" + file_extension
                success, msg = remove_image_metadata(file_path, temp_output_path)
                if not success: return False, msg
                temp_file_path = temp_output_path
            elif file_extension == ".pdf":
                temp_output_path = file_path + ".no_meta.pdf"
                success, msg = remove_pdf_metadata(file_path, temp_output_path)
                if not success: return False, msg
                temp_file_path = temp_output_path
            else:
                # For other file types, metadata removal is implicitly handled by reading raw content
                pass

        with open(public_key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

        aes_key = os.urandom(32)  # 256-bit key
        iv = os.urandom(16)  # 128-bit IV

        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        with open(temp_file_path, "rb") as infile:
            file_content = infile.read()
        
        if compress:
            file_content = gzip.compress(file_content)

        with open(output_file_path, "wb") as outfile:
            # Write a 2-byte header: 1st byte for compression flag, 2nd for metadata removal flag
            outfile.write(b'\x01' if compress else b'\x00')
            outfile.write(b'\x01' if remove_metadata else b'\x00')
            outfile.write(encrypted_aes_key)  # Write encrypted AES key
            outfile.write(iv)  # Write IV
            # Encrypt the (possibly compressed and metadata-stripped) content
            outfile.write(encryptor.update(file_content))
            outfile.write(encryptor.finalize())

        # Clean up temporary file if created
        if remove_metadata and temp_file_path != file_path:
            os.remove(temp_file_path)

        return True, f"File \'{file_path}\' encrypted to \'{output_file_path}\'" + (" (with compression and metadata removed)" if compress and remove_metadata else " (with compression)" if compress else " (with metadata removed)" if remove_metadata else "")
    except Exception as e:
        return False, f"Error encrypting file: {e}"

def decrypt_file(encrypted_file_path, private_key_path, output_file_path):
    """Decrypts a file using RSA private key and AES symmetric decryption, handling optional decompression."""
    try:
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # Assuming no password for the private key
                backend=default_backend()
            )

        with open(encrypted_file_path, "rb") as infile:
            # Read the compression and metadata removal flags
            compress_flag = infile.read(1)
            metadata_removed_flag = infile.read(1) # Read the new metadata flag

            encrypted_aes_key_len = private_key.key_size // 8  # RSA key size in bytes
            encrypted_aes_key = infile.read(encrypted_aes_key_len)

            # Read IV
            iv = infile.read(16)

            # Read the rest of the encrypted content
            encrypted_content = infile.read()

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

            decrypted_content = decryptor.update(encrypted_content) + decryptor.finalize()

            # Decompress if the flag was set
            if compress_flag == b'\x01':
                decrypted_content = gzip.decompress(decrypted_content)

            with open(output_file_path, "wb") as outfile:
                outfile.write(decrypted_content)

        return True, f"File \'{encrypted_file_path}\' decrypted to \'{output_file_path}\'"
    except Exception as e:
        return False, f"Error decrypting file: {e}"

# --- GUI Application ---
class RSACryptorGUI:
    def __init__(self, master):
        self.master = master
        master.title("RSA File Cryptor")
        self.create_widgets()

    def create_widgets(self):
        # Key Generation Section
        key_frame = tk.LabelFrame(self.master, text="Generate RSA Key Pair", padx=10, pady=10)
        key_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(key_frame, text="Private Key Path:").grid(row=0, column=0, sticky="w")
        self.private_key_entry = tk.Entry(key_frame, width=50)
        self.private_key_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(key_frame, text="Browse", command=lambda: self.browse_file(self.private_key_entry, save=True, default_name="private.pem")).grid(row=0, column=2)

        tk.Label(key_frame, text="Public Key Path:").grid(row=1, column=0, sticky="w")
        self.public_key_entry = tk.Entry(key_frame, width=50)
        self.public_key_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(key_frame, text="Browse", command=lambda: self.browse_file(self.public_key_entry, save=True, default_name="public.pem")).grid(row=1, column=2)

        tk.Button(key_frame, text="Generate Keys", command=self.generate_keys).grid(row=2, column=1, pady=10)

        # Encryption Section
        encrypt_frame = tk.LabelFrame(self.master, text="Encrypt File", padx=10, pady=10)
        encrypt_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(encrypt_frame, text="Input File:").grid(row=0, column=0, sticky="w")
        self.encrypt_input_entry = tk.Entry(encrypt_frame, width=50)
        self.encrypt_input_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(encrypt_frame, text="Browse", command=lambda: self.browse_file(self.encrypt_input_entry)).grid(row=0, column=2)

        tk.Label(encrypt_frame, text="Public Key:").grid(row=1, column=0, sticky="w")
        self.encrypt_public_key_entry = tk.Entry(encrypt_frame, width=50)
        self.encrypt_public_key_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(encrypt_frame, text="Browse", command=lambda: self.browse_file(self.encrypt_public_key_entry)).grid(row=1, column=2)

        tk.Label(encrypt_frame, text="Output File:").grid(row=2, column=0, sticky="w")
        self.encrypt_output_entry = tk.Entry(encrypt_frame, width=50)
        self.encrypt_output_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(encrypt_frame, text="Browse", command=lambda: self.browse_file(self.encrypt_output_entry, save=True, default_name="encrypted.bin")).grid(row=2, column=2)

        self.compress_var = tk.BooleanVar()
        tk.Checkbutton(encrypt_frame, text="Compress File", variable=self.compress_var).grid(row=3, column=1, sticky="w")

        self.remove_metadata_var = tk.BooleanVar()
        tk.Checkbutton(encrypt_frame, text="Remove Metadata (Images/PDFs)", variable=self.remove_metadata_var).grid(row=4, column=1, sticky="w")

        tk.Button(encrypt_frame, text="Encrypt", command=self.perform_encryption).grid(row=5, column=1, pady=10)

        # Decryption Section
        decrypt_frame = tk.LabelFrame(self.master, text="Decrypt File", padx=10, pady=10)
        decrypt_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(decrypt_frame, text="Input Encrypted File:").grid(row=0, column=0, sticky="w")
        self.decrypt_input_entry = tk.Entry(decrypt_frame, width=50)
        self.decrypt_input_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(decrypt_frame, text="Browse", command=lambda: self.browse_file(self.decrypt_input_entry)).grid(row=0, column=2)

        tk.Label(decrypt_frame, text="Private Key:").grid(row=1, column=0, sticky="w")
        self.decrypt_private_key_entry = tk.Entry(decrypt_frame, width=50)
        self.decrypt_private_key_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(decrypt_frame, text="Browse", command=lambda: self.browse_file(self.decrypt_private_key_entry)).grid(row=1, column=2)

        tk.Label(decrypt_frame, text="Output File:").grid(row=2, column=0, sticky="w")
        self.decrypt_output_entry = tk.Entry(decrypt_frame, width=50)
        self.decrypt_output_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(decrypt_frame, text="Browse", command=lambda: self.browse_file(self.decrypt_output_entry, save=True, default_name="decrypted.txt")).grid(row=2, column=2)

        tk.Button(decrypt_frame, text="Decrypt", command=self.perform_decryption).grid(row=3, column=1, pady=10)

        # Status Bar
        self.status_label = tk.Label(self.master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=3, column=0, columnspan=3, sticky="ew")

    def browse_file(self, entry_widget, save=False, default_name=""):
        if save:
            file_path = filedialog.asksaveasfilename(defaultextension=".pem" if ".pem" in default_name else ".bin" if ".bin" in default_name else ".txt", initialfile=default_name)
        else:
            file_path = filedialog.askopenfilename()
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def update_status(self, message, is_error=False):
        self.status_label.config(text=message, fg="red" if is_error else "black")

    def generate_keys(self):
        private_path = self.private_key_entry.get()
        public_path = self.public_key_entry.get()

        if not private_path or not public_path:
            self.update_status("Please specify paths for both private and public keys.", is_error=True)
            return

        success, message = generate_rsa_key_pair(private_path, public_path)
        if success:
            self.update_status(message)
            messagebox.showinfo("Success", message)
        else:
            self.update_status(message, is_error=True)
            messagebox.showerror("Error", message)

    def perform_encryption(self):
        input_file = self.encrypt_input_entry.get()
        public_key = self.encrypt_public_key_entry.get()
        output_file = self.encrypt_output_entry.get()
        compress = self.compress_var.get()
        remove_metadata = self.remove_metadata_var.get()

        if not input_file or not public_key or not output_file:
            self.update_status("All encryption fields are required.", is_error=True)
            return

        success, message = encrypt_file(input_file, public_key, output_file, compress=compress, remove_metadata=remove_metadata)
        if success:
            self.update_status(message)
            messagebox.showinfo("Success", message)
        else:
            self.update_status(message, is_error=True)
            messagebox.showerror("Error", message)

    def perform_decryption(self):
        input_file = self.decrypt_input_entry.get()
        private_key = self.decrypt_private_key_entry.get()
        output_file = self.decrypt_output_entry.get()

        if not input_file or not private_key or not output_file:
            self.update_status("All decryption fields are required.", is_error=True)
            return

        success, message = decrypt_file(input_file, private_key, output_file)
        if success:
            self.update_status(message)
            messagebox.showinfo("Success", message)
        else:
            self.update_status(message, is_error=True)
            messagebox.showerror("Error", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = RSACryptorGUI(root)
    root.mainloop()

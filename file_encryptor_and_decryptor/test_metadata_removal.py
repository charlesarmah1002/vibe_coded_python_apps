
from rsa_gui_cryptor import remove_image_metadata, remove_pdf_metadata
from PIL import Image
import pikepdf
import os

def test_metadata_removal():
    print("Testing Metadata Removal logic...")
    
    # 1. Test Image Metadata Removal
    img = Image.new('RGB', (100, 100), color = 'red')
    # Add some dummy EXIF data if possible, but even just saving and reloading strips it in our implementation
    img.save('test_meta.jpg', exif=b'Some dummy exif data')
    
    success, msg = remove_image_metadata('test_meta.jpg', 'test_no_meta.jpg')
    print(msg)
    
    # 2. Test PDF Metadata Removal
    pdf = pikepdf.Pdf.new()
    with pdf.open_metadata() as meta:
        meta['dc:title'] = 'Test Title'
    pdf.save('test_meta.pdf')
    
    success, msg = remove_pdf_metadata('test_meta.pdf', 'test_no_meta.pdf')
    print(msg)
    
    with pikepdf.open('test_no_meta.pdf') as pdf_check:
        if not pdf_check.docinfo:
            print("SUCCESS: PDF metadata removed!")
        else:
            print("FAILURE: PDF metadata still exists.")

if __name__ == "__main__":
    test_metadata_removal()

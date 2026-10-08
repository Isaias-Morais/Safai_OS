"""
SafaiOS Cryptographic & Perceptual Hashing Utility
Computes MD5, SHA256, and 64-bit Difference Hash (dHash) for perceptual image deduplication.
"""
import hashlib
from PIL import Image

def compute_md5(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def compute_sha256(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def compute_dhash(file_path, hash_size=8):
    """
    Computes 64-bit Difference Hash (dHash) for an image file.
    """
    try:
        with Image.open(file_path) as img:
            # Convert to grayscale and resize to (hash_size + 1, hash_size)
            img = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
            pixels = list(img.tobytes())
            
            difference = []
            for row in range(hash_size):
                for col in range(hash_size):
                    left_pixel = pixels[row * (hash_size + 1) + col]
                    right_pixel = pixels[row * (hash_size + 1) + col + 1]
                    difference.append(left_pixel > right_pixel)
            
            # Convert boolean array to hex string
            decimal_value = 0
            for bit in difference:
                decimal_value = (decimal_value << 1) | bit
            return f"{decimal_value:016x}"
    except Exception as e:
        return f"error_{e}"

def hamming_distance(hash1_hex, hash2_hex):
    """
    Computes Hamming distance between two 16-hex character dHash strings.
    """
    if len(hash1_hex) != 16 or len(hash2_hex) != 16:
        return 64
    val1 = int(hash1_hex, 16)
    val2 = int(hash2_hex, 16)
    return bin(val1 ^ val2).count("1")

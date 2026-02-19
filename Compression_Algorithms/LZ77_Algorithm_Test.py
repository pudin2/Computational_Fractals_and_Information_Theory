import pathlib
import tkinter as tk
from tkinter import filedialog

from LZ77_Algorithm import (
    compress_lz77, decompress_lz77,
    tokens_to_bytes, bytes_to_tokens
)

def seleccionar_archivo_pdf() -> pathlib.Path:

    root = tk.Tk()
    root.withdraw() 

    ruta = filedialog.askopenfilename(
        title="Select the file",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    if not ruta:
        raise SystemExit("No file selected.")

    return pathlib.Path(ruta)


def main():

    in_path = seleccionar_archivo_pdf()

    if not in_path.exists():
        raise FileNotFoundError(f"File do not exist: {in_path}")

    print(f"File selected: {in_path}")

    data = in_path.read_bytes()

    tokens = compress_lz77(data, window_size=8192, lookahead_size=32)

    recovered = decompress_lz77(tokens)
    assert recovered == data, "Failed:decompresion do not reconstruct the file exactly."

    compressed_blob = tokens_to_bytes(tokens)

    roundtrip_tokens = bytes_to_tokens(compressed_blob)
    assert decompress_lz77(roundtrip_tokens) == data, "Failed: unreversible token serialization."

    original_size = len(data)
    compressed_size = len(compressed_blob)
    ratio = compressed_size / original_size

    print("\nOK ✅ Roundtrip .")
    print(f"File: {in_path.name}")
    print(f"Original bytes:   {original_size:,}")
    print(f"LZ77 bytes:       {compressed_size:,}")
    print(f"Compression ratio (LZ77/original): {ratio:.4f}")
    print(f"Space saving: {100*(1-ratio):.2f}% (if positive)")


if __name__ == "__main__":
    main()

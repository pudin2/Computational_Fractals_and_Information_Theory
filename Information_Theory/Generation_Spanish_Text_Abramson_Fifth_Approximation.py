import re
import random
import pathlib
import tkinter as tk
from tkinter import filedialog
from pdfminer.high_level import extract_text


def seleccionar_pdf() -> pathlib.Path:
    root = tk.Tk()
    root.withdraw()            
    root.attributes("-topmost", True)  

    ruta = filedialog.askopenfilename(
        title="Select the PDF (corpus in Spanish)",
        initialdir=str(pathlib.Path.home() / "Documents"),
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    root.destroy()  

    if not ruta:
        raise SystemExit("No file selected.")
    return pathlib.Path(ruta)


def extraer_texto_pdf(pdf_path: pathlib.Path) -> str:
    return extract_text(str(pdf_path))


def tokenizar_espanol(texto: str) -> list[str]:
    texto = texto.lower()
    return re.findall(r"[a-záéíóúüñ]+", texto, flags=re.IGNORECASE)


def construir_distribucion(tokens: list[str], min_len: int = 1) -> tuple[list[str], list[float]]:
    if min_len > 1:
        tokens = [w for w in tokens if len(w) >= min_len]

    freq = {}
    for w in tokens:
        freq[w] = freq.get(w, 0) + 1

    palabras = list(freq.keys())
    conteos = [freq[w] for w in palabras]
    total = sum(conteos)
    probs = [c / total for c in conteos]
    return palabras, probs


def generar_quinta_aproximacion(palabras: list[str], probs: list[float], n_palabras: int = 400) -> str:
    muestra = random.choices(palabras, weights=probs, k=n_palabras)

    lineas = []
    linea = []
    for w in muestra:
        linea.append(w)
        if len(linea) >= 12:
            lineas.append(" ".join(linea))
            linea = []
    if linea:
        lineas.append(" ".join(linea))
    return "\n".join(lineas)


def main():
    pdf_path = seleccionar_pdf()
    print(f"PDF selected: {pdf_path}")

    texto = extraer_texto_pdf(pdf_path)
    tokens = tokenizar_espanol(texto)

    if len(tokens) < 1000:
        print("Warning: the PDF extracted few tokens; the result could be poor.")

    palabras, probs = construir_distribucion(tokens)

    salida = generar_quinta_aproximacion(palabras, probs, n_palabras=500)

    out_path = pdf_path.with_suffix(".quinta_aprox.txt")
    out_path.write_text(salida, encoding="utf-8")

    print("\nText generated (sample):\n")
    print(salida[:1200], "...\n")
    print(f"Saved in: {out_path}")


if __name__ == "__main__":
    main()

import unicodedata as ud
import zlib
from dataclasses import dataclass

COMB_ACUTE = "\u0301"      
COMB_GRAVE = "\u0300"      
COMB_HOOK  = "\u0309"      
COMB_TILDE = "\u0303"      
COMB_DOT   = "\u0323"      

COMB_BREVE = "\u0306"      
COMB_CIRC  = "\u0302"      
COMB_HORN  = "\u031B"      
COMB_STROKE = "\u0335"     


TONE_TO_ID = {
    None: 0,
    COMB_ACUTE: 1,
    COMB_GRAVE: 2,
    COMB_HOOK:  3,
    COMB_TILDE: 4,
    COMB_DOT:   5,
}
ID_TO_TONE = {v: k for k, v in TONE_TO_ID.items()}

VQ_TO_ID = {None: 0, COMB_BREVE: 1, COMB_CIRC: 2, COMB_HORN: 3}
ID_TO_VQ = {v: k for k, v in VQ_TO_ID.items()}

BASES = ["a", "e", "i", "o", "u", "y", "d", "_"]
BASE_TO_ID = {ch: i for i, ch in enumerate(BASES)}
ID_TO_BASE = {i: ch for ch, i in BASE_TO_ID.items()}

@dataclass
class PackedChar:
    base_id: int   
    vq_id: int     
    tone_id: int   
    is_upper: int  
    is_d_stroke: int  


def pack_pc(pc: PackedChar) -> bytes:

    b = (pc.base_id & 0b111) << 5
    b |= (pc.vq_id & 0b11) << 3
    b |= (pc.tone_id & 0b111)
    meta = (pc.is_upper & 1) << 1 | (pc.is_d_stroke & 1)
    return bytes([b, meta])


def unpack_pc(data: bytes, i: int) -> tuple[PackedChar, int]:
    b = data[i]
    meta = data[i+1]
    base_id = (b >> 5) & 0b111
    vq_id = (b >> 3) & 0b11
    tone_id = b & 0b111
    is_upper = (meta >> 1) & 1
    is_d_stroke = meta & 1
    return PackedChar(base_id, vq_id, tone_id, is_upper, is_d_stroke), i + 2


def encode_vietnamese(text: str) -> bytes:

    out = bytearray()
    for ch in text:

        if ch in ("đ", "Đ"):
            base = "d"
            is_upper = 1 if ch == "Đ" else 0
            pc = PackedChar(BASE_TO_ID[base], 0, 0, is_upper, 1)
            out.append(0x00)
            out.extend(pack_pc(pc))
            continue

        nfd = ud.normalize("NFD", ch)
        base = nfd[0]
        marks = nfd[1:]

        base_lower = base.lower()
        if base_lower in BASE_TO_ID and base_lower != "_":

            vq = None
            tone = None
            for m in marks:
                if m in (COMB_BREVE, COMB_CIRC, COMB_HORN):
                    vq = m
                elif m in (COMB_ACUTE, COMB_GRAVE, COMB_HOOK, COMB_TILDE, COMB_DOT):
                    tone = m

            pc = PackedChar(
                base_id=BASE_TO_ID[base_lower],
                vq_id=VQ_TO_ID.get(vq, 0),
                tone_id=TONE_TO_ID.get(tone, 0),
                is_upper=1 if base.isupper() else 0,
                is_d_stroke=0
            )
            out.append(0x00)
            out.extend(pack_pc(pc))
        else:

            b = ch.encode("utf-8")
            out.append(0xFF)
            out.append(len(b))
            out.extend(b)

    return bytes(out)


def decode_vietnamese(data: bytes) -> str:
    out_chars = []
    i = 0
    while i < len(data):
        tag = data[i]
        i += 1
        if tag == 0x00:
            pc, i = unpack_pc(data, i)
            base = ID_TO_BASE[pc.base_id]

            if pc.is_d_stroke == 1 and base == "d":
                ch = "Đ" if pc.is_upper else "đ"
                out_chars.append(ch)
                continue

            ch_base = base.upper() if pc.is_upper else base
            parts = [ch_base]
            vq = ID_TO_VQ.get(pc.vq_id)
            tone = ID_TO_TONE.get(pc.tone_id)
            if vq:
                parts.append(vq)
            if tone:
                parts.append(tone)

            out_chars.append(ud.normalize("NFC", "".join(parts)))
        elif tag == 0xFF:
            ln = data[i]; i += 1
            b = data[i:i+ln]; i += ln
            out_chars.append(b.decode("utf-8"))
        else:
            raise ValueError(f"Unknown tag: {tag}")

    return "".join(out_chars)

def compress_vietnamese(text: str, level: int = 9) -> bytes:
    raw = encode_vietnamese(text)
    return zlib.compress(raw, level)

def decompress_vietnamese(blob: bytes) -> str:
    raw = zlib.decompress(blob)
    return decode_vietnamese(raw)


if __name__ == "__main__":
    samples = [
        "Tiếng Việt có dấu: Tôi đang học ở trường.",
        "Cộng hòa Xã hội chủ nghĩa Việt Nam.",
        "đ Đ ă â ê ô ơ ư á à ả ã ạ ấ ầ ẩ ẫ ậ"
    ]

    for s in samples:
        enc = encode_vietnamese(s)
        dec = decode_vietnamese(enc)
        assert dec == s, (s, dec)

        comp = compress_vietnamese(s)
        decomp = decompress_vietnamese(comp)
        assert decomp == s, (s, decomp)

        print("OK:", s)
        print("  bytes utf-8:", len(s.encode("utf-8")))
        print("  bytes encoded:", len(enc))
        print("  bytes compressed:", len(comp))

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Token:
    offset: int
    length: int
    next_byte: int | None  


def _find_longest_match(data: bytes, pos: int, window_size: int, lookahead_size: int) -> Tuple[int, int]:

    start = max(0, pos - window_size)
    window = data[start:pos]
    lookahead = data[pos:pos + lookahead_size]

    best_length = 0
    best_offset = 0

    if not window or not lookahead:
        return 0, 0

    for w_i in range(len(window)):
        length = 0

        while (length < len(lookahead)) and (w_i + length < len(window)) and (window[w_i + length] == lookahead[length]):
            length += 1

        if length > best_length:
            best_length = length

            best_offset = len(window) - w_i

        if best_length == len(lookahead):
            break

    if best_length == 0:
        return 0, 0

    return best_offset, best_length


def compress_lz77(data: bytes, window_size: int = 4096, lookahead_size: int = 18) -> List[Token]:

    tokens: List[Token] = []
    pos = 0
    n = len(data)

    while pos < n:
        offset, length = _find_longest_match(data, pos, window_size, lookahead_size)

        if offset == 0 or length == 0:
            # literal: (0,0,byte)
            tokens.append(Token(0, 0, data[pos]))
            pos += 1
        else:
            next_pos = pos + length
            next_byte = data[next_pos] if next_pos < n else None
            tokens.append(Token(offset, length, next_byte))
            pos = next_pos + (1 if next_byte is not None else 0)

    return tokens


def decompress_lz77(tokens: List[Token]) -> bytes:

    out = bytearray()

    for tok in tokens:
        if tok.offset == 0 and tok.length == 0:
            if tok.next_byte is None:
                raise ValueError("Inalid Literal Token: next_byte=None")
            out.append(tok.next_byte)
            continue

        if tok.offset <= 0 or tok.length <= 0:
            raise ValueError(f"Token inválido: {tok}")

        start = len(out) - tok.offset
        if start < 0:
            raise ValueError(f"Offset fuera de rango: {tok.offset} con salida len={len(out)}")

        # Copia con posible solapamiento
        for i in range(tok.length):
            out.append(out[start + i])

        if tok.next_byte is not None:
            out.append(tok.next_byte)

    return bytes(out)


def tokens_to_bytes(tokens: List[Token]) -> bytes:
    
    out = bytearray()
    for t in tokens:
        if not (0 <= t.offset <= 65535):
            raise ValueError("offset out of range for this serialization")
        if not (0 <= t.length <= 255):
            raise ValueError("length out of range for this serialization")

        out.append((t.offset >> 8) & 0xFF)
        out.append(t.offset & 0xFF)
        out.append(t.length & 0xFF)

        if t.next_byte is None:
            out.append(1)
        else:
            out.append(0)
            out.append(t.next_byte & 0xFF)

    return bytes(out)


def bytes_to_tokens(blob: bytes) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(blob):
        if i + 4 > len(blob):
            raise ValueError("Truncated Blob")
        offset = (blob[i] << 8) | blob[i + 1]
        length = blob[i + 2]
        flag = blob[i + 3]
        i += 4

        if flag == 1:
            tokens.append(Token(offset, length, None))
        elif flag == 0:
            if i >= len(blob):
                raise ValueError("Blob truncated (next_byte needed)")
            next_byte = blob[i]
            i += 1
            tokens.append(Token(offset, length, next_byte))
        else:
            raise ValueError("Invalid Flag")

    return tokens

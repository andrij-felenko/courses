# Декодер LZ77: розгортає потік трійок (offset, length, next) назад у дані.
# out — буфер виходу, який заразом служить «словником»: копіюємо з нього ж.
def lz77_decode(triples):
    out = bytearray()                     # росте разом зі «словником»
    for off, length, nxt in triples:
        # копіюємо length символів із уже відновленого хвоста (по одному —
        # це важливо: збіг може накладатися сам на себе, див. нижче)
        for _ in range(length):
            out.append(out[len(out) - off])
        if nxt is not None:               # і дописуємо свіжий символ, якщо він є
            out.append(nxt)
    return bytes(out)

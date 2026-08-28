CLEAN, FIXED, DETECTED = "CLEAN", "FIXED", "DETECTED"

def decode(w):
    """Повертає (вердикт, слово, місце). Слово — виправлена копія або та сама."""
    srow, scol = syndromes(w)
    bad_rows = [r for r, s in enumerate(srow) if s]
    bad_cols = [c for c, s in enumerate(scol) if s]

    # тотожність: XOR усіх рядкових синдромів = XOR усіх стовпцевих = парність слова
    assert len(bad_rows) % 2 == len(bad_cols) % 2

    if not bad_rows and not bad_cols:
        return CLEAN, w, None

    if len(bad_rows) == 1 and len(bad_cols) == 1:
        r, c = bad_rows[0], bad_cols[0]
        out = [row[:] for row in w]
        out[r][c] ^= 1
        return FIXED, out, (r, c)

    return DETECTED, w, None

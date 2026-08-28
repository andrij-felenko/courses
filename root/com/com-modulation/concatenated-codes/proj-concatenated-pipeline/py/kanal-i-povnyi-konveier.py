def channel(bits, start, length, rng):
    """Пакет: у смузі завади кожен біт перевертається з імовірністю ½."""
    out = list(bits)
    for i in range(start, min(start + length, len(out))):
        if rng.random() < 0.5:
            out[i] ^= 1
    return out

def pipeline(data, burst_len, burst_at, rng, use_interleaver=True):
    rows = [rs_encode(data[r * K:(r + 1) * K], NSYM) for r in range(DEPTH)]   # зовнішній
    stream = interleave(rows) if use_interleaver else flat(rows)              # перемішування
    sent = inner_encode(stream)                                              # внутрішній
    got = channel(sent, burst_at, burst_len, rng)                           # канал
    stream2 = inner_decode(got)                                             # внутрішній⁻¹
    rows2 = deinterleave(stream2) if use_interleaver else unflat(stream2)   # перемішування⁻¹
    damage = [sum(a != b for a, b in zip(rows[r], rows2[r])) for r in range(DEPTH)]
    out = []
    for r in range(DEPTH):
        dec, _ = rs_decode(rows2[r], NSYM)                                  # зовнішній⁻¹
        if dec is None:
            return None, damage
        out.extend(dec[:K])
    return out, damage

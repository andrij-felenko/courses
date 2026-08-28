def minimal_poly(e, taken):
    conj = []                            # спряжені: e, 2e, 4e, … (mod N)
    c = e
    while c not in conj:
        conj.append(c); taken.add(c); c = (c * 2) % N
    poly = [1]                           # ∏ (x − α^c), коефіцієнти low→high
    for c in conj:
        r = antilog[c]
        nxt = [0] * (len(poly) + 1)
        for i, coef in enumerate(poly):
            nxt[i]     ^= gf_mul(coef, r)   # * (−α^c) = * α^c у GF(2)
            nxt[i + 1] ^= coef              # * x
        poly = nxt
    return poly                          # коефіцієнти гарантовано двійкові

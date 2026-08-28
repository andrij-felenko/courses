# ── 4) торнадо: гойдаємо один множник, решту тримаємо на номіналі ──
def tornado(factors):
    bars = []
    for f in factors:
        v_lo = nominal(factors); v_lo[f.name] = f.lo
        v_hi = nominal(factors); v_hi[f.name] = f.hi
        o_lo, o_hi = peak_rps(v_lo), peak_rps(v_hi)
        bars.append((f.name, o_lo, o_hi, abs(o_hi - o_lo)))
    bars.sort(key=lambda b: b[3], reverse=True)   # найдовший розмах згори
    return bars

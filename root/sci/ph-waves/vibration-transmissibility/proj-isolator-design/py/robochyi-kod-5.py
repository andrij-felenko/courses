def sweep_ascii(zeta: float, rmin=0.2, rmax=10.0, cols=54, rows=15) -> None:
    """Крива T(r) по смузі як ASCII-графік (лог-осі)."""
    from math import log10
    lr0, lr1 = log10(rmin), log10(rmax)
    tvals = [transmissibility(rmin * (rmax / rmin) ** (i / (cols - 1)), zeta)
             for i in range(cols)]
    tmax = max(tvals + [1.0])
    lt0, lt1 = log10(0.01), log10(max(tmax, 10.0))
    grid = [[" "] * cols for _ in range(rows)]

    def row_of(t):
        f = (log10(max(t, 1e-3)) - lt0) / (lt1 - lt0)
        return min(rows - 1, max(0, rows - 1 - int(round(f * (rows - 1)))))

    r1_row = row_of(1.0)                 # лінія T = 1
    for c in range(cols):
        grid[r1_row][c] = "-"
    c_sqrt2 = int(round((log10(R_THRESH) - lr0) / (lr1 - lr0) * (cols - 1)))
    for rr in range(rows):               # вертикаль r = √2
        if grid[rr][c_sqrt2] == " ":
            grid[rr][c_sqrt2] = ":"
    for c, t in enumerate(tvals):
        grid[row_of(t)][c] = "*"

    print(f"  T(r) для ζ = {zeta:g}   (│ вісь T лог, r лог; ─ T=1; : r=√2)")
    for rr in range(rows):
        print("   │" + "".join(grid[rr]))
    print("   └" + "─" * cols)
    print(f"    r={rmin:g}" + " " * (cols - 12) + f"r={rmax:g}")


def compare_zeta(exc_hz: float, fn_hz: float, zetas, order=1.0) -> None:
    """Та сама опора (fₙ фіксована) — що дає кожне ζ. Парадокс загасання."""
    r = exc_hz / fn_hz
    print(f"── Одна опора fₙ = {fn_hz:.1f} Гц, трясіння {exc_hz:.1f} Гц "
          f"(r = {r:.2f}) — вплив ζ ──")
    print(f"  {'ζ':>6} │ {'T роб.':>7} │ {'ізол.':>6} │ {'пік на пуску':>13}")
    print("  " + "─" * 6 + "─┼─" + "─" * 7 + "─┼─" + "─" * 6 + "─┼─" + "─" * 13)
    for z in zetas:
        t = transmissibility(r, z)
        _, pt = resonance_peak(z)
        print(f"  {z:>6.3f} │ {t:>7.3f} │ {100*(1-t):>5.0f}% │ {pt:>10.1f}×")

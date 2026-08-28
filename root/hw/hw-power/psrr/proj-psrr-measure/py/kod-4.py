def sweep(awg, scope):
    n = int(round(math.log10(F_STOP / F_START) * PER_DEC))
    state = {"vpp": 0.05, "out_pp": 0.2}
    rows = []
    for i in range(n + 1):
        r = measure_point(awg, scope, F_START * 10 ** (i / PER_DEC), state)
        solid = r["margin"] > MARGIN_MIN
        print("%9.1f Гц  PSRR %6.2f дБ%s  вх %6.1f мВpp  вих %8.3f мВpp  "
              "запас %5.1f дБ  N=%d"
              % (r["f"], r["psrr"], " " if solid else " ‼", r["in_pp"] * 1e3,
                 r["out_pp"] * 1e3, r["margin"], r["n"]))
        if not solid:
            print("            ↑ вихід тоне в шумі — це стеля стенда, а не PSRR: "
                  "чесно казати «глибше за %.1f дБ»" % r["ceiling"])
        rows.append(r)
    return rows


def thru(awg, scope, freqs=(100.0, 1e4, 1e6)):
    """Обидва щупи на ОДИН вузол. Має вийти 0 дБ; що вийшло — то розбіг каналів."""
    state = {"vpp": 0.5, "out_pp": 0.3}
    for f0 in freqs:
        r = measure_point(awg, scope, f0, state)
        print("%9.0f Гц: розбіг каналів %+.2f дБ" % (f0, r["psrr"]))


def main():
    rm = pyvisa.ResourceManager()
    awg = Awg(rm.open_resource("USB0::0x0957::0x2C07::MY52815943::INSTR"))
    scope = Scope(rm.open_resource("USB0::0x2A8D::0x1797::CN59356102::INSTR"))
    try:
        rows = sweep(awg, scope)
    finally:
        awg.off()                                    # не лишати брижі на шині
    with open("psrr.csv", "w", encoding="utf-8") as fh:
        fh.write("f_Hz,psrr_dB,vin_pp_V,vout_pp_V,margin_dB\n")
        for r in rows:
            fh.write("%.3f,%.3f,%.6f,%.9f,%.2f\n"
                     % (r["f"], r["psrr"], r["in_pp"], r["out_pp"], r["margin"]))


if __name__ == "__main__":
    main()

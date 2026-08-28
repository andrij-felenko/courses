if __name__ == "__main__":
    p = point(FACTORS)
    lo, hi = interval(FACTORS)
    mc = monte_carlo(FACTORS)

    print(f"поріг (1 сервер):     {THRESHOLD:.0f} запитів/с")
    print(f"точкова (номінал):    {p:.0f} запитів/с   (запас x{THRESHOLD/p:.2f})")
    print(f"інтервал (край-край): {lo:.0f} .. {hi:.0f} запитів/с")
    side = ("весь ЛІВОРУЧ порога" if hi <= THRESHOLD
            else "весь ПРАВОРУЧ порога" if lo >= THRESHOLD
            else "НАКРИВАЄ поріг")
    print(f"  -> {side}\n")

    print("Монте-Карло (n=100000):")
    print(f"  P50={pct(mc,50):.0f}  P90={pct(mc,90):.0f}  P95={pct(mc,95):.0f}  "
          f"середнє={sum(mc)/len(mc):.0f}")
    print(f"  P(перевищить поріг) = {100*frac_over(mc, THRESHOLD):.0f}%\n")

    print("Торнадо (внесок у розкид):")
    widest = max(b[3] for b in tornado(FACTORS)) or 1.0
    for name, o_lo, o_hi, sw in tornado(FACTORS):
        bar = "#" * int(round(sw / widest * 36))
        mark = "  <-- накриває поріг" if o_lo < THRESHOLD < o_hi else ""
        print(f"  {name:10s} {o_lo:5.0f}..{o_hi:<5.0f} |{bar:36s}| Δ={sw:5.0f}{mark}")

def find_center_robust(max_gap: int) -> int:
    pf_map = sweep(RANGE_MAX)

    despeckle(pf_map, max_gap)             # прибрати шумові провали
    w = widest_window(pf_map)

    kind = classify(w, len(pf_map))
    if kind is WinKind.WIN_NONE:
        return -1                          # канал не заводиться
    elif kind in (WinKind.WIN_CLIP_LO, WinKind.WIN_CLIP_HI):
        report_clip()                      # діагностика: око за межею діапазону
                                           # (рішення — далі; тут беремо що є)
    # WIN_OK — нічого додатково не робимо
    return (w.lo + w.hi) // 2

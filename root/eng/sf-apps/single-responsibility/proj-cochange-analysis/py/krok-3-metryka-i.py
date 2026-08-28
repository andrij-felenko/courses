def rank(file_count, pair_count, min_support=3, min_conf=0.5):
    """Пари над порогами, орієнтовані за сильнішим боком, від сильних до слабких."""
    rows = []
    for (a, b), support in pair_count.items():
        if support < min_support:
            continue
        conf_a = support / file_count[a]      # впевненість a ⇒ b
        conf_b = support / file_count[b]      # впевненість b ⇒ a
        if conf_a >= conf_b:                  # орієнтуємо за сильнішим боком
            src, dst, conf, rev = a, b, conf_a, conf_b
        else:
            src, dst, conf, rev = b, a, conf_b, conf_a
        if conf < min_conf:
            continue
        rows.append((conf, support, rev, src, dst))
    rows.sort(reverse=True)
    return rows

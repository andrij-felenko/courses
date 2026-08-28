TTLS = [0, 1, 5, 30, 60, 300, 600]

def report(events):
    for cls, sh in SHAPES.items():
        n_top, n_keys, share = hot_set_share(events, cls)
        print(f"\n=== {cls}  (бюджет несвіжості {sh['budget']} с) ===")
        print(f"ворота 2 — перекіс: топ {n_top}/{n_keys} ключів = {share:.0%} читань")
        for ttl in TTLS:
            hr, qps = simulate(events, cls, ttl)
            factor = "∞" if qps == 0 else f"{sh['rps']/qps:,.0f}×"
            print(f"  TTL {ttl:>4} с  влучність {hr:6.1%}  "
                  f"QPS джерела {qps:7.2f}  розвантаження {factor:>6}")

def recommend(events):
    for cls, sh in SHAPES.items():
        _, _, share = hot_set_share(events, cls)
        allowed = max(t for t in TTLS if t <= sh["budget"])   # найбільший TTL у бюджеті
        hr, _ = simulate(events, cls, allowed)
        if sh["budget"] == 0:
            verdict = "без TTL-кешу — лише скид на запис"
        elif share < 0.30:
            verdict = "кеш сумнівний — доступ надто розмазаний"
        else:
            verdict = f"кешуй, TTL={allowed} с → влучність {hr:.0%}"
        print(f"{cls:>10}: перекіс {share:4.0%} | бюджет {sh['budget']:>4} с | {verdict}")

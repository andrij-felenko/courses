def mono_demo(pin):
    c = Cluster([0.2, 0.5, 1.0])
    r = ReadRouter(c, sticky=False, pin=pin, rng=Rng(7))  # sticky off → device_state завжди на фоловер
    val, seen_max, viol = "off", -1, 0
    for i in range(600):
        if i % 5 == 0:                        # писар перемикає стан кожні 0.1 с
            val = "on" if val == "off" else "off"
            c.write(0, 0, val)
        got = r.route(0, "device_state").get(0, 0)   # спостерігач опитує живий стан
        seq = got[1] if got else -1
        if seq < seen_max: viol += 1          # побачив стан, СТАРШИЙ за вже бачений
        seen_max = max(seen_max, seq)
        c.tick(0.02)
    return viol

print(mono_demo(pin=True), mono_demo(pin=False))   # → 0 379

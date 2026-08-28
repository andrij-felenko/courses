def measure_point(awg, scope, f0, state):
    """Один вимір: підігнати інжекцію й шкалу, захопити, повернути PSRR."""
    cycles = min(max(f0 * 0.02, 20), 2000)
    gen, out_pp, got = state["vpp"], state["out_pp"], None

    for _ in range(6):
        awg.set(f0, gen)
        scope.set_scale(1, max(VIN_TARGET_PP, 0.02))
        scope.set_scale(2, out_pp)
        time.sleep(0.15)                             # інжектор має устоятися
        (v1, dt, clip1), (v2, _, clip2) = scope.capture(f0, cycles)

        if clip2:                                    # вихідна шкала завузька
            out_pp *= 4
            continue
        if clip1:                                    # інжекція зашкалює вхідний канал
            gen *= 0.5
            continue

        a_in = abs(amp_at(v1, dt, f0))
        a_out = abs(amp_at(v2, dt, f0))
        got = (v2, dt, a_in, a_out)
        out_pp = max(4 * a_out, 6e-3)                # запас: синус плюс шум

        in_pp = 2 * a_in
        if 0.7 * VIN_TARGET_PP <= in_pp <= 1.4 * VIN_TARGET_PP or gen >= GEN_VPP_MAX:
            break
        gen = min(gen * VIN_TARGET_PP / max(in_pp, 1e-9), GEN_VPP_MAX)

    if got is None:
        raise RuntimeError("f=%.0f Гц: не вдалося зняти чистий запис" % f0)

    v2, dt, a_in, a_out = got
    noise = floor_at(v2, dt, f0)
    state["vpp"], state["out_pp"] = gen, out_pp
    return {
        "f": f0,
        "psrr": 20 * math.log10(a_in / a_out),
        "in_pp": 2 * a_in,
        "out_pp": 2 * a_out,
        "margin": 20 * math.log10(a_out / noise),    # наскільки вихід вищий за шум
        "ceiling": 20 * math.log10(a_in / noise),    # найглибше, що стенд узагалі покаже
        "n": len(v2),
    }

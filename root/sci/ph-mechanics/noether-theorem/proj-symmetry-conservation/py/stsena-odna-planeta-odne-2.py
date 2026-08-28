def integrate(step, dt, n_orbits=20):
    q, v = q0.copy(), v0.copy()
    E0, L0 = energy(q, v), ang_mom(q, v)
    dE_max = dL_max = r_max = 0.0
    for _ in range(int(n_orbits * 2*np.pi / dt)):
        q, v = step(q, v, dt)                       # один крок обраного методу
        dE_max = max(dE_max, abs(energy(q, v) - E0))
        dL_max = max(dL_max, abs(ang_mom(q, v) - L0))
        r_max  = max(r_max,  np.hypot(*q))
    return energy(q, v), dE_max, dL_max, r_max

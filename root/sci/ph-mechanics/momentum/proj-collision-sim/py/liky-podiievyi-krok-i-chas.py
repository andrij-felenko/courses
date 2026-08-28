def run_events(bodies, T, e=1.0):
    """Провести світ до часу T, зупиняючись точно на кожному ударі."""
    t = 0.0
    while t < T:
        soon, pair = T - t, None                  # найпізніше — просто дожити до T
        n = len(bodies)
        for i in range(n):
            for j in range(i + 1, n):
                tc = time_to_contact(bodies[i], bodies[j])
                if tc is not None and tc < soon:
                    soon, pair = tc, (i, j)
        for b in bodies:
            b.x += b.v * soon                     # адванс УСІХ рівно до події
        t += soon
        if pair:
            i, j = pair
            resolve(bodies[i], bodies[j], e)      # рівно один удар

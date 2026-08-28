def fly(v0, angle_deg, m, Cd, A, step=rk4_step, dt=0.01):
    "Кидаємо тіло під кутом, крокуємо до приземлення, вертаємо зведення польоту."
    accel = make_accel(m, Cd, A)
    th = np.radians(angle_deg)
    r = np.array([0.0, 0.0])
    v = v0*np.array([np.cos(th), np.sin(th)])
    t = apex = t_apex = 0.0
    while True:
        r1, v1 = step(r, v, accel, dt)
        if r1[1] < 0:                          # перетнули землю
            f = r[1] / (r[1] - r1[1])          # частка кроку до y = 0
            r_land = r + f*(r1 - r)
            v_land = v + f*(v1 - v)
            t += f*dt
            return dict(range=r_land[0], t=t, apex=apex, t_apex=t_apex,
                        v_land=np.hypot(*v_land),
                        ang_land=np.degrees(np.arctan2(-v_land[1], v_land[0])))
        if v[1] >= 0 and v1[1] < 0:            # верхівка дуги
            apex, t_apex = r1[1], t
        r, v = r1, v1
        t += dt

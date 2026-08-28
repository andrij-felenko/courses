def restart_demo(rebuild):
    c = Cluster([0.2, 0.5, 1.0]); r = ReadRouter(c)
    c.write(0, 0, "on");  r.note_write(0)         # початково on усюди
    for _ in range(60): c.tick(0.02)              # +1.2 с: усі фоловери догнали
    c.write(0, 0, "off"); r.note_write(0)         # користувач ВИМИКАЄ (t0)
    for _ in range(5): c.tick(0.02)               # +0.1 с
    r.last_write.clear()                          # ← РЕСТАРТ: пам'ять вікна втрачено
    if rebuild: r.last_write[0] = c.clock.t       # грейс: вважати дім щойно-писаним
    for _ in range(3): c.tick(0.02)               # +0.16 с — час перечитати екран
    node = r.route(0, "device_state")
    got = node.get(0, 0)
    return ("лідер" if node is c.leader else "фоловер"), (got[0] if got else None)

print(restart_demo(False), restart_demo(True))    # → ('фоловер', 'on') ('лідер', 'off')

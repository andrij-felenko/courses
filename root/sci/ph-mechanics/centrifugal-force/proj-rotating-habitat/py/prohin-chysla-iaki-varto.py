def _self_test():
    s = design_min_radius(1.0, 2.0)
    assert abs(s.g_fraction() - 1.0) < 1e-9 and abs(s.rpm() - 2.0) < 1e-9
    assert abs(rad_to_rpm(rpm_to_rad(3.7)) - 3.7) < 1e-12        # рад/с ↔ об/хв оборотні
    h = at_radius(1.0, 100.0)
    assert abs(h.coriolis_frac(1.3) - 2*1.3/h.rim_speed()) < 1e-12
    vb = Habitat(r=38.0, omega=rpm_to_rad(3.0))                   # колесо фон Брауна 1952
    assert abs(vb.g_fraction() - 0.382) < 0.01                   # «третина g»
    print("самоперевірки пройдено\n")


if __name__ == "__main__":
    _self_test()

    print("== станція на повне земне g ==")
    for lim in (2.0, 4.0):
        s = design_min_radius(1.0, lim)
        print(f"межа {lim:.0f} об/хв → радіус {s.r:5.1f} м (∅ {2*s.r:.0f} м), "
              f"обід {s.rim_speed():4.1f} м/с, період {s.period():4.1f} с, "
              f"градієнт {s.gradient_frac()*100:.1f}%")

    print("\n== колесо фон Брауна (1952): діаметр 76 м, 3 об/хв ==")
    vb = Habitat(r=38.0, omega=rpm_to_rad(3.0))
    print(f"тяжіння {vb.g_fraction():.2f} g,  обід {vb.rim_speed():.1f} м/с,  "
          f"період {vb.period():.1f} с,  Коріоліс {vb.coriolis_frac()*100:.0f}% ваги  → {vb.verdict()}")

    print("\n== таблиця варіантів на повне g ==")
    variants_table(1.0, [500, 224, 100, 50, 20, 10, 5])

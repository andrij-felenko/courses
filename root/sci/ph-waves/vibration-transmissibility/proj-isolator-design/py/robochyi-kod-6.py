if __name__ == "__main__":
    d = design_mount(mass_kg=40.0, target_T=0.10, zeta=0.05, rpm=1800.0, order=1.0)
    report(d, mounts=4)
    print()
    sweep_ascii(zeta=d.zeta)
    print()
    compare_zeta(exc_hz=d.exc_hz, fn_hz=d.fn_hz,
                 zetas=[0.02, 0.05, 0.15, 0.30, 0.70])
    print()
    r_naive = sqrt(1.0 + 1.0 / 0.10)          # r² = 1 + 1/T (без загасання)
    r_exact = ratio_for_target(0.10, 0.05)
    t_at_naive = transmissibility(r_naive, 0.05)
    print("── Наївне сортування (без загасання) проти точного ──")
    print(f"  без ζ:  r = {r_naive:.3f}  → але реальне T при ζ=0.05: "
          f"{t_at_naive:.3f}  (ціль 0.100 промазана)")
    print(f"  з ζ:    r = {r_exact:.3f}  → T точно 0.100 (опора трохи м'якша)")

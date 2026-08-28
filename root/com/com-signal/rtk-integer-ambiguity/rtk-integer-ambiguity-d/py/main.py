LAMBDA_L1 = 0.190293   # довжина хвилі GPS L1, метри


def range_from_phase(N: int, phi_cycles: float) -> float:
    """Відстань уздовж променя за цілим N і виміряною дробовою фазою phi (у циклах)."""
    return (N + phi_cycles) * LAMBDA_L1


def main() -> None:
    N_true = 128      # справжнє число цілих хвиль
    phi = 0.37        # дробова частина, виміряна точно

    r_true = range_from_phase(N_true,     phi)
    r_off1 = range_from_phase(N_true + 1, phi)   # схибили на 1 цикл
    r_off3 = range_from_phase(N_true - 3, phi)   # схибили на 3 цикли

    print(f"правильно:      {r_true:.4f} m")
    print(f"помилка +1:     {r_off1:.4f} m  (зсув {(r_off1 - r_true) * 100.0:.1f} cm)")
    print(f"помилка -3:     {r_off3:.4f} m  (зсув {(r_off3 - r_true) * 100.0:.1f} cm)")


if __name__ == "__main__":
    main()

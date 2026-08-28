def main() -> None:
    systems = [
        # АНАЛОГ: нема кодера/декодера; радіо стале (одне число → lo=hi).
        # Домінує сенсор камери; ~19 мс разом.
        FpvSystem(name="Аналог",
                  sensor=SpanMs(12, 12), encode=SpanMs(0, 0),
                  radio=SpanMs(2, 2), decode=SpanMs(0, 0), display=SpanMs(5, 5),
                  fps=60),

        # HDZERO: однобічний, фіксована затримка; кодек є, але без пересилань
        # радіо стале. ~14 мс при 100 к/с.
        FpvSystem(name="HDZero",
                  sensor=SpanMs(3, 3), encode=SpanMs(4, 4),
                  radio=SpanMs(3, 3), decode=SpanMs(2, 2), display=SpanMs(2, 2),
                  fps=100),

        # DJI O4 (гоночний режим): двобічний, але в гонці радіо майже без
        # розкиду; ~15 мс скло-скло.
        FpvSystem(name="DJI O4 (race)",
                  sensor=SpanMs(3, 3), encode=SpanMs(4, 5),
                  radio=SpanMs(2, 3), decode=SpanMs(3, 3), display=SpanMs(3, 3),
                  fps=100),

        # WALKSNAIL: двобічний; у полі ~22 мс, за бетоном ~35 мс через
        # пересилання — радіо тримає ШИРОКИЙ діапазон.
        FpvSystem(name="Walksnail",
                  sensor=SpanMs(4, 4), encode=SpanMs(6, 7),
                  radio=SpanMs(6, 18), decode=SpanMs(4, 4), display=SpanMs(2, 2),
                  fps=120),
    ]

    speed = 120.0   # км/год — типова гоночна

    for s in systems:
        report(s, speed)


if __name__ == "__main__":
    main()

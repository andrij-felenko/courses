mu = MU_WATER
def R(r_mm, L_cm):                            # зручний конструктор опору з міліметрів
    return pipe_resistance(r_mm * 1e-3, L_cm * 1e-2, mu)

pipes = [
    ("A", "B", R(1.0, 10)),                   # 2.55·10⁸
    ("A", "C", R(0.8, 10)),                   # 6.22·10⁸
    ("B", "C", R(0.6, 10)),                   # 1.96·10⁹  ← місток (найвужчий → найтвердіший)
    ("B", "D", R(0.8, 10)),                   # 6.22·10⁸
    ("C", "D", R(1.0, 10)),                   # 2.55·10⁸
]
pressures = {"A": 1000.0, "D": 0.0}           # Па
p, Q = solve_network(pipes, pressures)

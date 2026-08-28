def moment_of_inertia(masses, distances):
    # J = Σ mᵢ · ρᵢ²  — рецепт напряму: сума по всіх частинках
    return sum(m * r * r for m, r in zip(masses, distances))

# точкова маса 0.5 кг на відстані 0.4 м від осі
print(moment_of_inertia([0.5], [0.4]))          # 0.5·0.4² = 0.08 кг·м²

# стрижень M = 2 кг, L = 1 м, вісь на кінці:
# ріжемо на N смужок і сумуємо mᵢ·ρᵢ² — має вийти M·L²/3
M, L, N = 2.0, 1.0, 200_000
dm = M / N                                        # маса однієї смужки
dx = L / N
masses    = [dm] * N
distances = [(i + 0.5) * dx for i in range(N)]    # центр кожної смужки
J = moment_of_inertia(masses, distances)
print(round(J, 6), "≈", round(M * L**2 / 3, 6))   # 0.666667 ≈ 0.666667

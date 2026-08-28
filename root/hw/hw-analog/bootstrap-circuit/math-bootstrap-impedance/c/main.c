// Видимий вхідний опір бутстрепа та його чутливість до дрейфу A.
// r_node — опір, що множиться (Ом); a — коефіцієнт передачі (0..1);
// da — очікуваний дрейф A (напр. 0.002). Заповнює z (Ом) і spread (відносний розкид).
void bootstrap_zin(float r_node, float a, float da, float *z, float *spread)
{
    float one_minus_a = 1.0f - a;
    if (one_minus_a < 1e-4f) one_minus_a = 1e-4f;  // біля A=1 формула вибухає — обмежуємо
    *z = r_node / one_minus_a;            // Z = R / (1 − A)
    *spread = da / one_minus_a;           // ΔZ/Z ≈ ΔA / (1 − A): крихкість виграшу
}
// bootstrap_zin(25000, 0.99f, 0.002f, &z, &s):  z ≈ 2.5 МОм, s ≈ 0.20 (±20%) — робоча точка
// bootstrap_zin(25000, 0.999f, 0.002f, &z, &s): z ≈ 25 МОм, s ≈ 2.0 (±200%) — красиво й непридатно

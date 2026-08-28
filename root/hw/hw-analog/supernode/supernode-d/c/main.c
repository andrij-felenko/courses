// Суперузол на два вузли: вхідний струм I у вузол A, резистори R1 (A→земля),
// R3 (B→земля) і джерело напруги E між A і B (плюсом до A: V_a − V_b = E).
// Рівняння суперузла:  V_a/R1 + V_b/R3 = I
// Обмеження джерела:    V_a − V_b = E   →   V_a = V_b + E
// Підставляємо:        (V_b + E)/R1 + V_b/R3 = I
// Звідси V_b, далі V_a. Опори в омах, струм в амперах, напруги у вольтах.
typedef struct { float v_a, v_b; } NodeVolts;

NodeVolts supernode_solve(float I, float R1, float R3, float E)
{
    float g1 = 1.0f / R1;                       // провідності гілок на землю
    float g3 = 1.0f / R3;
    float v_b = (I - E * g1) / (g1 + g3);       // розв'язок щодо V_b
    NodeVolts r;
    r.v_b = v_b;
    r.v_a = v_b + E;                            // обмеження джерела
    return r;
}
// supernode_solve(6e-3, 2e3, 3e3, 3.0f) -> v_a ≈ 8.4 В, v_b ≈ 5.4 В

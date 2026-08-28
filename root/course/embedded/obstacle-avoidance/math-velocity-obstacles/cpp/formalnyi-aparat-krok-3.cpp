// Апарат A у p_A, перешкода B у p_B (центри), радіуси r_A, r_B, швидкість B — v_B.
// Питання: чи веде обрана швидкість v_A у зіткнення (v_A ∈ VO)?
struct Vec { float x, y; };

bool velocity_in_vo(Vec vA, Vec vB, Vec pA, Vec pB,
                    float rA, float rB) {
    // Вісь конуса: напрям від A до центра B, і відстань між центрами.
    float dx = pB.x - pA.x, dy = pB.y - pA.y;
    float d  = sqrtf(dx*dx + dy*dy);
    if (d <= rA + rB) return true;        // уже дотик/перекриття — небезпека завжди

    float ex = dx / d, ey = dy / d;       // одинична вісь ê

    // Піввкут конуса: sin α = (r_A + r_B)/d  →  cos α = √(1 − sin²α).
    float sin_a = (rA + rB) / d;
    float cos_a = sqrtf(1.0f - sin_a*sin_a);

    // Відносна швидкість w = v_A − v_B (вектор від апекса конуса до v_A).
    float wx = vA.x - vB.x, wy = vA.y - vB.y;
    float wlen = sqrtf(wx*wx + wy*wy);
    if (wlen < 1e-6f) return false;       // стоїмо відносно B — не зближуємося

    // w у конусі ⟺ кут(w, ê) ≤ α ⟺ (w·ê)/|w| ≥ cos α.
    float cos_w = (wx*ex + wy*ey) / wlen;
    return cos_w >= cos_a;                // true → швидкість веде в зіткнення
}

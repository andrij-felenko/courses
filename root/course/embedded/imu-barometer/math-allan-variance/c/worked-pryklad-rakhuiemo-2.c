// tau[j], sa[j] — j-й рядок таблиці (τ у с, σ_A у °/с); K рядків усього
// (a) ARW: σ_A на ділянці −1/2 при τ = 1 с. Беремо рядок з τ, найближчим до 1 с.
int    j1 = 0;
double best = 1e9;
for (int j = 0; j < K; j++) {
    double dist = fabs(tau[j] - 1.0);         // наскільки далеко від 1 с
    if (dist < best) { best = dist; j1 = j; }
}
double ARW = sa[j1] * 60.0;                    // °/√год   (×60: √с → √год)

// (b) нестабільність зсуву: мінімум кривої × 0.664, у °/год
double sa_min = sa[0];
for (int j = 1; j < K; j++)
    if (sa[j] < sa_min) sa_min = sa[j];        // найнижча точка полиці
double bias_instab = sa_min * 0.664 * 3600.0;  // °/год  (×3600: /с → /год)

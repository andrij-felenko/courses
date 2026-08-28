// Струм лінії з активної потужності та коефіцієнта потужності.
// I = P / (U · PF);   S = U · I = P / PF.
float power_active_w   = 2200.0f;   // корисна потужність, Вт
float voltage_rms_v    = 230.0f;    // діюче значення напруги, В
float power_factor     = 0.82f;     // повний PF (зсув × спотворення)

float current_a        = power_active_w / (voltage_rms_v * power_factor);
float power_apparent_va = power_active_w / power_factor;

// current_a        = 2200 / (230 · 0.82) = 2200 / 188.6 ≈ 11.7 А
// power_apparent_va = 2200 / 0.82        ≈ 2683 В·А

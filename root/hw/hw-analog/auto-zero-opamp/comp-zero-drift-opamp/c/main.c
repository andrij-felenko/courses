// Вихідна похибка нуля = (Vos + dVos/dT · ΔT) · підсилення
float gain = 100.0f;       // підсилення тракту
float dT   = 30.0f;        // прогрів, °C

// Звичайний прецизійний ОП
float vos_ord   = 100e-6f;     // зсув 100 мкВ
float drift_ord = 1.5e-6f;     // дрейф 1.5 мкВ/°C
float err_ord = (vos_ord + drift_ord * dT) * gain;
// = (100e-6 + 1.5e-6*30) * 100 = (100e-6 + 45e-6)*100 = 0.0145 В  → 14.5 мВ

// Zero-drift ОП (типові числа класу)
float vos_zd   = 5e-6f;        // зсув 5 мкВ
float drift_zd = 0.02e-6f;     // дрейф 0.02 мкВ/°C = 20 нВ/°C
float err_zd = (vos_zd + drift_zd * dT) * gain;
// = (5e-6 + 0.02e-6*30) * 100 = (5e-6 + 0.6e-6)*100 = 0.00056 В  → 0.56 мВ

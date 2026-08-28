// Вихідна похибка = (зсув + дрейф·ΔT) · підсилення
float gain = 1000.0f;     // підсилення тракту
float dT   = 40.0f;       // зміна температури, °C

// Звичайний прецизійний ОП
float vos_ord    = 150e-6f;    // зсув 150 мкВ
float drift_ord  = 1.0e-6f;    // дрейф 1 мкВ/°C
float err_ord = (vos_ord + drift_ord * dT) * gain;
// = (150e-6 + 1e-6*40) * 1000 = (150e-6 + 40e-6)*1000 = 0.190 В

// Zero-drift ОП (типу ADA4528)
float vos_zd    = 2.5e-6f;     // зсув 2.5 мкВ
float drift_zd  = 0.015e-6f;   // дрейф 0.015 мкВ/°C
float err_zd = (vos_zd + drift_zd * dT) * gain;
// = (2.5e-6 + 0.015e-6*40) * 1000 = (2.5e-6 + 0.6e-6)*1000 = 0.0031 В

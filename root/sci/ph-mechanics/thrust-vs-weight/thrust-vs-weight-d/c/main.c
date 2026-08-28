// оберти зависання з квадратичної моделі T = k_T·n²
float T_max   = 8.0f;      // Н на повному газі
float n_max   = 400.0f;    // об/с на повному газі
float T_hover = 2.94f;     // Н на гвинт, щоб висіти

float k_T   = T_max / (n_max * n_max);        // коефіцієнт тяги гвинта
float n_hov = sqrtf(T_hover / k_T);           // оберти зависання
float throttle_hover = n_hov / n_max;         // частка газу на завис

// n_hov ≈ 242 об/с  →  throttle_hover ≈ 0.61

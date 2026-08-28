// Оцінка втрат на body-діоді нижнього ключа за мертвий час.
// Запускаємо на МК (ESP32 тощо) для теплового нагляду в реальному часі.
const float Vf      = 0.8f;       // пряме падіння body-діода, В (з даташита)
const float I_load  = 5.0f;       // струм навантаження, А
const float f_sw    = 100000.0f;  // частота перемикання, Гц
const float t_dead  = 60e-9f;     // мертвий час, с (один проміжок)
const int   n_dead  = 2;          // скільки разів за період діод проводить

// частка періоду, коли струм іде крізь діод
float duty_diode = t_dead * n_dead * f_sw;     // 60e-9 * 2 * 1e5 = 0.012  (1.2 %)
float p_diode    = Vf * I_load * duty_diode;   // 0.8 * 5 * 0.012 = 0.048 Вт

ESP_LOGI("pwr", "vtraty na body-diodi: %.0f mVt (%.1f%% periodu)",
         p_diode * 1000.0f, duty_diode * 100.0f);
// → vtraty na body-diodi: 48 mVt (1.2% periodu)

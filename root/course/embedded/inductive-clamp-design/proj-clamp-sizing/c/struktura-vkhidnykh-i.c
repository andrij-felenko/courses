#include <math.h>
#include <stdbool.h>
#include <stdint.h>

// Вхідні дані задачі. Одиниці СІ скрізь, крім частоти (Гц) — як підписано.
typedef struct {
    double inductance_H;   // індуктивність навантаження L, генрі
    double current_A;      // робочий струм крізь котушку I₀, ампери
    double supply_V;       // напруга живлення V_жив, вольти
    double t_off_target_s; // бажаний час вимкнення t_off, секунди
    double bv_dss_V;       // пробивна напруга ключа BV_DSS, вольти
    double winding_ohm;    // активний опір обмотки R, Ом (для діод-кламп)
    double pwm_freq_Hz;    // частота комутації f, Гц; 0 = разове спрацювання
} clamp_input_t;

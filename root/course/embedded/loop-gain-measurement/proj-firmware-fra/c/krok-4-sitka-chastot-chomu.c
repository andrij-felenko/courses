// Одна точка виміряної кривої: частота й виміряні модуль і фаза.
typedef struct { float f, mag_db, phase_deg; } fra_point_t;

// Логарифмічна сітка: points_per_decade точок на кожну декаду від f_start до f_stop.
// Кожна наступна частота = попередня × сталий множник. Пишемо в масив {f, mag, phase}.
void sweep_loop(float f_start, float f_stop, int points_per_decade,
                float fs, fra_point_t *out, int max_pts, int *out_n)
{
    float ratio = powf(10.0f, 1.0f / points_per_decade);  // множник між сусідніми точками
    float amp_ceiling = 0.02f;   // стеля збурення: 2% керування (межа лінійності)
    int   i = 0;

    for (float f = f_start; f <= f_stop && i < max_pts; f *= ratio) {
        // 1) підібрати амплітуду під цю частоту (над шумом, під нелінійністю)
        float amp = pick_amplitude(f, fs, amp_ceiling, /*snr_min=*/16.0f);

        // 2) скільки періодів накопичити: на низьких частотах період довгий,
        //    тож менше циклів — інакше вимір тягнеться вічність (див. пастку часу).
        uint32_t cycles = (f < 100.0f) ? 8u : (f < 2000.0f) ? 16u : 32u;

        // 3) виміряти точку й покласти її в масив разом із частотою
        loop_point_t lp = measure_point(f, fs, cycles, amp);
        out[i].f         = f;
        out[i].mag_db    = lp.mag_db;
        out[i].phase_deg = lp.phase_deg;
        i++;
    }
    *out_n = i;
}

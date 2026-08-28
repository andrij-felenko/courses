#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Параметри автогенератора на мості Віна */
#define FREQ_HZ       1000.0f
#define DT            1.0e-6f        /* Крок інтегрування: 1 мкс */
#define TOTAL_STEPS   25000          /* 25 мс моделювання */
#define V_SAT         5.0f           /* Напруга насичення ОП (В) */
#define GAIN_SMALL    3.40f          /* Підсилення малого сигналу (A_start) */

/* Нелінійна характеристика підсилювача з плавним насиченням (tanh) */
static float amplifier_transfer(float v_in) {
    float linear_gain = GAIN_SMALL;
    return V_SAT * tanhf((linear_gain * v_in) / V_SAT);
}

int main(void) {
    float omega0 = 2.0f * (float)M_PI * FREQ_HZ;
    float v_out = 0.0f;
    float v_fb = 0.0f;       /* Напруга на виході моста Віна */
    float v_fb_dot = 0.0f;   /* Перша похідна напруги зворотного зв'язку */

    /* Ініціалізація початкового мікровольтового теплового шуму */
    v_fb = 10.0e-6f; 

    printf("Час (мс)\tV_вихід (В)\tV_зз (В)\tСтатус\n");

    for (int step = 0; step < TOTAL_STEPS; ++step) {
        float time_ms = (float)step * DT * 1000.0f;

        /* Підсилювач формує вихідну напругу з нелінійним насиченням */
        v_out = amplifier_transfer(v_fb);

        /* Диференціальне рівняння другого порядку для смугового моста Віна:
           d²v_fb/dt² + 3·ω₀·(dv_fb/dt) + ω₀²·v_fb = ω₀·(dv_out/dt) */
        float dv_out_dt = (step > 0) ? (v_out - amplifier_transfer(v_fb - v_fb_dot * DT)) / DT : 0.0f;
        float v_fb_ddot = omega0 * dv_out_dt - 3.0f * omega0 * v_fb_dot - omega0 * omega0 * v_fb;

        /* Числове інтегрування методом Ейлера–Крамера */
        v_fb_dot += v_fb_ddot * DT;
        v_fb += v_fb_dot * DT;

        /* Вивід кожні 2.5 мс для контролю динаміки */
        if (step % 2500 == 0) {
            const char* status = (fabsf(v_out) < 0.1f) ? "Наростання" :
                                 (fabsf(v_out) > 4.5f) ? "Стаціонарний (граничний цикл)" : "Перехідний режим";
            printf("%.2f\t\t%.4f\t\t%.4f\t\t%s\n", time_ms, v_out, v_fb, status);
        }
    }

    return 0;
}

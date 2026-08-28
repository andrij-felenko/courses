#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PAL_SAMPLE_RATE_HZ 17734475.0
#define PAL_LINE_SAMPLES    1135
#define PAL_F_SC_HZ        4433618.75
#define PI                 3.14159265358979323846

/* Рівні напруги у квантах 8-бітного ЦАП */
#define DAC_SYNC_TIP       0
#define DAC_BLANKING       73
#define DAC_WHITE_100      255
#define DAC_BURST_AMP      36

/* Структура параметрів однієї кольорової смуги (75% EBU) */
typedef struct {
    float y_norm;      /* Нормована яскравість 0.0 .. 1.0 */
    float u_norm;      /* Компонент U */
    float v_norm;      /* Компонент V */
} ColorBarEBU;

static const ColorBarEBU EBU_BARS[8] = {
    { 0.75f,  0.000f,  0.000f }, /* Білий 75% */
    { 0.64f, -0.327f,  0.075f }, /* Жовтий */
    { 0.53f,  0.110f, -0.461f }, /* Ціан */
    { 0.41f, -0.217f, -0.386f }, /* Зелений */
    { 0.34f,  0.217f,  0.386f }, /* Пурпур */
    { 0.23f, -0.110f,  0.461f }, /* Червоний */
    { 0.11f,  0.327f, -0.075f }, /* Синій */
    { 0.00f,  0.000f,  0.000f }  /* Чорний */
};

/* Генерація одного телевізійного рядка PAL CVBS у буфер ЦАП */
void generate_pal_cvbs_line(uint8_t *buffer, uint32_t line_number) {
    bool is_v_inverted = (line_number % 2 != 0);
    double omega_sc = 2.0 * PI * PAL_F_SC_HZ / PAL_SAMPLE_RATE_HZ;
    double burst_phase_offset = is_v_inverted ? (3.0 * PI / 4.0) : (-3.0 * PI / 4.0);

    /* Часові межі у відліках (за Fs = 17.734475 МГц):
       Front Porch: 0..27 (1.5 мкс)
       Sync Tip:    27..110 (4.7 мкс)
       Breezeway:   110..126 (0.9 мкс)
       Color Burst: 126..170 (2.5 мкс, 10 періодів)
       Back Porch:  170..213 (2.4 мкс)
       Active Area: 213..1135 (52.0 мкс) */
    const uint32_t idx_sync_start  = 27;
    const uint32_t idx_sync_end    = 110;
    const uint32_t idx_burst_start = 126;
    const uint32_t idx_burst_end   = 170;
    const uint32_t idx_active_start = 213;

    for (uint32_t i = 0; i < PAL_LINE_SAMPLES; ++i) {
        if (i < idx_sync_start) {
            buffer[i] = DAC_BLANKING; /* Передній майданчик гасіння */
        } else if (i < idx_sync_end) {
            buffer[i] = DAC_SYNC_TIP; /* Рядковий синхроімпульс */
        } else if (i < idx_burst_start) {
            buffer[i] = DAC_BLANKING; /* Проміжний майданчик Breezeway */
        } else if (i < idx_burst_end) {
            /* Колірний спалах (Colorburst) на рівні гасіння */
            double burst_val = DAC_BURST_AMP * sin(omega_sc * (double)i + burst_phase_offset);
            int32_t sample = (int32_t)(DAC_BLANKING + burst_val + 0.5);
            buffer[i] = (uint8_t)(sample < 0 ? 0 : (sample > 255 ? 255 : sample));
        } else if (i < idx_active_start) {
            buffer[i] = DAC_BLANKING; /* Залишок заднього майданчика */
        } else {
            /* Активне відео: 8 смуг */
            uint32_t active_idx = i - idx_active_start;
            uint32_t bar_width = (PAL_LINE_SAMPLES - idx_active_start) / 8;
            uint32_t bar_idx = active_idx / bar_width;
            if (bar_idx > 7) bar_idx = 7;

            const ColorBarEBU *bar = &EBU_BARS[bar_idx];
            double y_dac = DAC_BLANKING + bar->y_norm * (DAC_WHITE_100 - DAC_BLANKING);

            /* Модуляція піднесучої: C(t) = U·sin(ωt) ± V·cos(ωt) */
            double v_sign = is_v_inverted ? -1.0 : 1.0;
            double u_mod = bar->u_norm * sin(omega_sc * (double)i);
            double v_mod = v_sign * bar->v_norm * cos(omega_sc * (double)i);
            double chroma_dac = (u_mod + v_mod) * (DAC_WHITE_100 - DAC_BLANKING);

            int32_t total_val = (int32_t)(y_dac + chroma_dac + 0.5);
            buffer[i] = (uint8_t)(total_val < 0 ? 0 : (total_val > 255 ? 255 : total_val));
        }
    }
}

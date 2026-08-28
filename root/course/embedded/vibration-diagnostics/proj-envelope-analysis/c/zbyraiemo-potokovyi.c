#include <math.h>

#define FS_RAW   20000.0f    // частота оцифровування, Гц
#define DECIM    10          // коефіцієнт децимації → 2 кГц на виході
#define ENV_N    512         // довжина буфера обвідної (для ШПФ)

static biquad_t bp1, bp2;    // смуговий фільтр (2 ланки = 24 дБ/окт)
static biquad_t lp;          // фільтр низьких частот (виділення обвідної)
static int   dec_cnt;
static float env_buf[ENV_N];
static volatile int env_idx;
static volatile int env_ready;

// Викликати один раз на старті.
void envelope_init(float f_res, float f_lp) {
    biquad_bandpass(&bp1, f_res, FS_RAW, 3.0f);   // широка смуга на резонансі
    biquad_bandpass(&bp2, f_res, FS_RAW, 3.0f);
    biquad_lowpass(&lp,  f_lp,  FS_RAW, 0.707f);  // Баттерворт
    dec_cnt = 0; env_idx = 0; env_ready = 0;
}

// Викликати на КОЖЕН сирий відлік прискорення (з ISR/DMA).
void envelope_feed(float x) {
    if (env_ready) return;                 // буфер ще не забрали — не псуємо

    float s = biquad_step(&bp1, x);        // 1) смуговий фільтр…
    s       = biquad_step(&bp2, s);        //    …другою ланкою
    s       = fabsf(s);                    // 2) випрямлення (демодуляція)
    s       = biquad_step(&lp, s);         // 3) фільтр низьких частот → обвідна

    if (++dec_cnt >= DECIM) {              // 2½) децимація
        dec_cnt = 0;
        env_buf[env_idx++] = s;
        if (env_idx >= ENV_N) {
            env_idx = 0;
            env_ready = 1;                 // обвідна готова — будимо основний цикл
        }
    }
}

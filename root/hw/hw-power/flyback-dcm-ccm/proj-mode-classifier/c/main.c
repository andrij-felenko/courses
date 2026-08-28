// Оцінка режиму flyback за виміряним струмом навантаження.
// Усе у фіксованій комі Q16.16; величини заздалегідь відмасштабовані.
// Lm_uH — намагнічувальна індукт. первинної, мкГн; n_q16 — Np/Ns у Q16.16.

#include <stdint.h>

typedef enum { MODE_DCM, MODE_BCM, MODE_CCM } fb_mode_t;

// Межовий вихідний струм (мА) за поточної робочої точки.
// Iбм[А] = n·Vin·D·(1−D) / (2·Lm·f).  Розкриваємо масштаби:
//   n = n_q16/2^16 ;  D·(1−D) = dd/2^16 ;  Lm[Гн]=Lm_uH·1e-6 ;  f[Гц]=f_khz·1e3.
// Отже Iбм[мА] = n_q16·Vin·dd·1e6 / ( 2^32 · 2 · Lm_uH · f_khz ).
static int32_t boundary_iout_ma(int32_t vin_v, int32_t d_q16,
                                int32_t n_q16, int32_t lm_uH, int32_t f_khz)
{
    int32_t one = (int32_t)(1 << 16);
    int64_t dd  = ((int64_t)d_q16 * (one - d_q16)) >> 16;   // D·(1−D) у Q16.16

    // Чисельник у 64 бітах. Стеж за розміром: n_q16·Vin·dd·1e6 для типових
    // (n≈4·2^16, Vin≈100, dd≈0.25·2^16, 1e6) ~ 4·10¹⁷ — влазить у int64 (< 9.2·10¹⁸),
    // але за великих Vin чи n перевіряй запас або зменшуй множник 1e6 → крок мА.
    int64_t num = (int64_t)n_q16 * vin_v * dd * 1000000LL;

    int64_t den = ((int64_t)1 << 32) * 2 * lm_uH * f_khz;
    if (den == 0) return 0;
    return (int32_t)(num / den);
}

// Класифікація з гістерезисом ±9%, щоб не «тремтіло» на самій межі.
static fb_mode_t classify_mode(int32_t iout_ma, int32_t vin_v, int32_t d_q16,
                               int32_t n_q16, int32_t lm_uH, int32_t f_khz)
{
    int32_t ibnd = boundary_iout_ma(vin_v, d_q16, n_q16, lm_uH, f_khz);
    int32_t hi = ibnd + (ibnd >> 4) + (ibnd >> 5);   // +~9%
    int32_t lo = ibnd - (ibnd >> 4) - (ibnd >> 5);   // −~9%
    if (iout_ma > hi) return MODE_CCM;               // струм вищий за межу → поличка є
    if (iout_ma < lo) return MODE_DCM;               // нижчий → осердя порожніє
    return MODE_BCM;                                 // у вузькій смузі — на межі
}

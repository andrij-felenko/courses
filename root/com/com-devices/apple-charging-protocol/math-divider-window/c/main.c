#include <stdbool.h>
#include <stdint.h>

typedef enum { SRC_UNKNOWN, SRC_500MA, SRC_1A, SRC_2A1, SRC_2A4 } src_class_t;

/* Міряємо не вольти, а ЧАСТКУ від VBUS — тоді розкид живлення й похибка
   опорної напруги скорочуються самі. adc_dp, adc_dm — сирі відліки з ліній
   D+/D−; adc_vb — відлік із дільника 1:2, підвішеного на саму VBUS. */

#define K_SCALE     1000   /* частка × 1000 */
#define K_2V0        400   /* 2.0/5.0 = 0.400 */
#define K_2V7        540   /* 2.7/5.0 = 0.540 */
#define K_TOL_PCT     10   /* ±10 %: паспорт джерела ⊕ дільник VBUS ⊕ нелінійність */

static int32_t k_of(uint32_t adc_line, uint32_t adc_vb)
{
    /* adc_vb міряє VBUS/2, тож повна шина — це 2·adc_vb */
    return (int32_t)((adc_line * (uint32_t)K_SCALE) / (2u * adc_vb));
}

static bool near_level(int32_t k, int32_t k_nom)
{
    int32_t tol = k_nom * K_TOL_PCT / 100;
    return k >= k_nom - tol && k <= k_nom + tol;
}

src_class_t classify_ratiometric(uint32_t adc_dp, uint32_t adc_dm, uint32_t adc_vb)
{
    if (adc_vb == 0) return SRC_UNKNOWN;      /* шина ще не піднялася */

    int32_t k_dp = k_of(adc_dp, adc_vb);
    int32_t k_dm = k_of(adc_dm, adc_vb);

    bool dp20 = near_level(k_dp, K_2V0), dp27 = near_level(k_dp, K_2V7);
    bool dm20 = near_level(k_dm, K_2V0), dm27 = near_level(k_dm, K_2V7);

    if (dp20 && dm20) return SRC_500MA;       /* слабке джерело   */
    if (dp20 && dm27) return SRC_1A;          /* Divider 1,  5 Вт */
    if (dp27 && dm20) return SRC_2A1;         /* Divider 2, 10 Вт */
    if (dp27 && dm27) return SRC_2A4;         /* Divider 3, 12 Вт */
    return SRC_UNKNOWN;
}

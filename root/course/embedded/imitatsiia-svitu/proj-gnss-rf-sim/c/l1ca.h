/* l1ca.h — два модулюючі потоки цивільного сигналу L1:
 * далекомірний код Голда (1023 чипи) і навігаційне повідомлення (50 біт/с). */
#ifndef L1CA_H
#define L1CA_H

#include <stdint.h>
#include <stdbool.h>

#include "ephemeris.h"

#define CA_CODE_LEN        1023
#define CA_CHIP_RATE_HZ    1023000.0
#define NAV_BIT_RATE_HZ    50.0
#define NAV_SUBFRAME_BITS  300
#define NAV_FRAME_BITS     1500          /* 5 підкадрів = 30 с */

/* Регістри G1/G2 з лінійним зворотним зв'язком; для кожного PRN — свої відводи. */
bool ca_code_generate(int prn, uint8_t out[CA_CODE_LEN]);

/* Секунда координації: поточна різниця UTC↔GPS і майбутня зі своєю датою. */
typedef struct {
    int delta_t_ls;      /* ΔtLS, чинна поправка */
    int delta_t_lsf;     /* ΔtLSF, поправка після стрибка */
    int wn_lsf;          /* тиждень уведення, 8 молодших біт */
    int dn;              /* день тижня, 1..7 */
} leap_info_t;

typedef struct {
    const nav_header_t *hdr;
    leap_info_t leap;
    uint8_t sv_health[32];   /* стан сузір'я для сторінки альманаху */
} nav_context_t;

typedef struct {
    uint8_t    bits[NAV_FRAME_BITS];
    gps_time_t start;        /* час першого біта кадру, кратний 30 с */
} nav_frame_t;

void nav_frame_build(nav_frame_t *fr, const ephemeris_t *e,
                     const nav_context_t *ctx, gps_time_t frame_start);

/* Номер біта в кадрі для моменту випромінювання; -1, якщо кадр застарів. */
int  nav_bit_index(const nav_frame_t *fr, gps_time_t t_tx);
int  nav_bit(const nav_frame_t *fr, long index);

#endif /* L1CA_H */

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>   // abs
#include <math.h>

// ── Калібрування радіоканалу (типові значення хобі-приймача) ──
#define RC_MIN        1000    // мкс: один край стіка
#define RC_MID        1500    // мкс: центр (стік відпущено)
#define RC_MAX        2000    // мкс: інший край
#define RC_DEADZONE     30    // мкс: віконце навколо центру, де віддаємо строгий 0
#define DRIVE_MAX     1000    // наш внутрішній діапазон: −1000..+1000

// Перевести сирий канал (мкс) у знакову величину −DRIVE_MAX..+DRIVE_MAX,
// з дедзоною навколо центру та жорстким обрізанням країв.
static int rc_to_signed(uint16_t us) {
    int centered = (int)us - RC_MID;           // тепер 0 = центр

    // 1) дедзона: усе близьке до центру — строгий нуль
    if (abs(centered) <= RC_DEADZONE) return 0;

    // 2) прибираємо саму ширину дедзони, щоб хід починався плавно з нуля,
    //    а не стрибав одразу на «дедзона × масштаб» одразу за краєм віконця
    if (centered > 0) centered -= RC_DEADZONE;
    else              centered += RC_DEADZONE;

    // 3) масштаб: півдіапазон каналу (500 мкс) мінус дедзона → DRIVE_MAX
    int span = (RC_MAX - RC_MID) - RC_DEADZONE; // 500 − 30 = 470
    int v = centered * DRIVE_MAX / span;

    // 4) жорстке обрізання: калібрування неточне, край каналу може бути 990 чи 2010
    if (v >  DRIVE_MAX) v =  DRIVE_MAX;
    if (v < -DRIVE_MAX) v = -DRIVE_MAX;
    return v;
}

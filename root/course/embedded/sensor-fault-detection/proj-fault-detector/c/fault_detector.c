// fault_detector.c
#include "fault_detector.h"
#include <math.h>     // isnan, isinf, fabsf

void fd_init(fd_channel_t *ch, const fd_config_t *cfg) {
    ch->cfg      = cfg;
    ch->state    = FD_TRUST;     // доки не доведено погане — віримо
    ch->reason   = FD_OK;
    ch->primed   = false;        // ще нема з чим порівнювати
    ch->last     = 0.0f;
    ch->last_ms  = 0u;
    ch->ref      = 0.0f;
    ch->still    = 0u;
    ch->bad_run  = 0u;
    ch->good_run = 0u;
}

// Миттєві перевірки одного відліку. Повертає FD_OK або причину «погано».
// На ПЕРШОМУ валідному відліку швидкість/завмер не судимо — нема об що.
static fd_reason_t fd_check_sample(fd_channel_t *ch, float x, uint32_t now_ms) {
    const fd_config_t *c = ch->cfg;

    // 1. Узагалі число? NaN/∞ ловимо першими, бо з ними решта порівнянь — сміття.
    if (isnan(x) || isinf(x)) return FD_NAN;

    // 2. У фізичних межах? Найгрубіша й найдешевша перевірка.
    if (x < c->min || x > c->max) return FD_RANGE;

    if (ch->primed) {
        // 3. Свіжість: чи не мовчав давач задовго до цього відліку.
        //    (now_ms - last_ms) у БЕЗЗНАКОВІЙ арифметиці коректно
        //    переживає переповнення лічильника часу — див. пастки.
        if ((now_ms - ch->last_ms) > c->timeout_ms) return FD_STALE;

        // 4. Швидкість: чи міг сигнал так стрибнути за один крок.
        if (fabsf(x - ch->last) > c->max_step) return FD_RATE;

        // 5. Завмер: рух менший за власний шум давача, і то надто довго.
        if (fabsf(x - ch->ref) < c->eps) {
            if (ch->still < 0xFFFFu) ch->still++;
            if (ch->still >= c->stuck_limit) return FD_STUCK;
        } else {
            ch->ref   = x;       // ворухнулося — оновлюємо опору
            ch->still = 0u;
        }
    }
    return FD_OK;
}

fd_state_t fd_update(fd_channel_t *ch, float x, uint32_t now_ms) {
    const fd_config_t *c = ch->cfg;
    fd_reason_t r = fd_check_sample(ch, x, now_ms);

    if (r == FD_OK) {
        // Добрий відлік. Запам'ятати його як базу для наступних перевірок.
        ch->last    = x;
        ch->last_ms = now_ms;
        if (!ch->primed) {       // ПЕРШИЙ валідний — розігріваємось
            ch->ref    = x;      // опора для завмеру
            ch->primed = true;
        }
        // Голос «добре» в лічильник довіри.
        ch->bad_run = 0u;
        if (ch->good_run < 0xFFFFu) ch->good_run++;
        ch->reason  = FD_OK;
        // Гістерезис угору: повертаємо довіру лише після HEAL добрих поспіль.
        if (ch->state == FD_FAULT && ch->good_run >= c->heal_count) {
            ch->state = FD_TRUST;
        }
    } else {
        // Поганий відлік. last/last_ms НЕ оновлюємо: брехливе число
        // не має ставати базою для майбутніх перевірок швидкості.
        ch->good_run = 0u;
        if (ch->bad_run < 0xFFFFu) ch->bad_run++;
        ch->reason   = r;
        // Гістерезис униз: оголошуємо відмову після TRIP поганих поспіль.
        if (ch->state == FD_TRUST && ch->bad_run >= c->trip_count) {
            ch->state = FD_FAULT;
        }
    }
    return ch->state;
}

bool        fd_is_valid(const fd_channel_t *ch) { return ch->state == FD_TRUST; }
fd_reason_t fd_reason  (const fd_channel_t *ch) { return ch->reason; }

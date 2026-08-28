#include <stdint.h>
#include <stdbool.h>

/* Стан присутності одного джерела — це і є наша машина станів. */
typedef enum {
    PRES_NEW = 0,   /* слот порожній, джерела ще не бачили */
    PRES_ALIVE,     /* удари приходять вчасно — мітка яскрава */
    PRES_LOST       /* тиша довше за поріг — мітка згасла, тривога */
} presence_t;

/* Усе, що сторож тримає про одне (SYS, COMP). */
typedef struct {
    bool        used;          /* слот зайнятий */
    uint8_t     sys;           /* system_id  джерела */
    uint8_t     comp;          /* component_id джерела */
    uint32_t    last_seen_ms;  /* час останнього HEARTBEAT від нього */
    uint32_t    period_ms;     /* оцінений період між його ударами */
    presence_t  state;         /* ALIVE / LOST */

    /* корисний контекст із самого серцебиття — для мітки на мапі */
    uint8_t     type;          /* MAV_TYPE: коптер / літак / ровер... */
    uint8_t     autopilot;     /* MAV_AUTOPILOT: ArduPilot / PX4... */
    uint8_t     base_mode;     /* службові прапорці (у т.ч. armed) */
    uint32_t    custom_mode;   /* число режиму конкретної прошивки */
} hb_source_t;

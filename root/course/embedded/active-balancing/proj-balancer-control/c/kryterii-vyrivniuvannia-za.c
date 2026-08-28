#include <stdint.h>
#include <stdbool.h>

#define N_CELLS   4

// Профіль хімії пакета — задається один раз під конкретні комірки.
typedef enum { CHEM_SLOPED, CHEM_FLAT } chem_kind_t;

typedef struct {
    chem_kind_t kind;        // похила (Li-ion) чи пласка (LiFePO4)
    uint16_t    knee_mv;     // напруга «зламу»: вище за неї напрузі можна вірити
    uint16_t    start_mv;    // поріг УВІМКНЕННЯ балансу (розкид criteria)
    uint16_t    stop_mv;     // поріг ВИМКНЕННЯ (гістерезис, < start_mv)
} chem_cfg_t;

// Приклади. Числа орієнтовні — під свої комірки уточнюй за даташитом.
static const chem_cfg_t CFG_LIION = {
    .kind = CHEM_SLOPED, .knee_mv = 0,    .start_mv = 30, .stop_mv = 10,
};
static const chem_cfg_t CFG_LFP = {
    .kind = CHEM_FLAT,   .knee_mv = 3450, .start_mv = 20, .stop_mv = 8,
};

// Стан вимірів: напруги комірок і поточна оцінка SOC (0..1000 = 0..100.0%).
typedef struct {
    uint16_t mv[N_CELLS];        // напруги, мВ
    uint16_t soc[N_CELLS];       // оцінка заряду, ‰ (проміле для цілочисельності)
    uint16_t pack_max_mv;        // найвища напруга в пакеті — щоб знати «де ми на кривій»
} pack_state_t;

// Порівнянна величина однієї комірки — те, що рівнятимемо між собою.
// Для похилої — це напруга в мВ. Для пласкої — SOC, перерахований у ту ж шкалу,
// щоб пороги start/stop лишались у звичних «мілівольтах розкиду».
static uint16_t cell_metric(const chem_cfg_t *c, const pack_state_t *p, int i)
{
    if (c->kind == CHEM_SLOPED)
        return p->mv[i];                       // напрузі віримо завжди

    // Пласка хімія: на плато напруга «сліпа» — беремо SOC.
    // Але якщо пакет дійшов до зламу, напруга знову інформативна й точніша.
    if (p->pack_max_mv >= c->knee_mv)
        return p->mv[i];                       // ми в зламі — повертаємось до напруги
    return p->soc[i];                          // на плато — рівняємо за зарядом
}

/* board_sim.h — модель плати для стенда.
 *
 * Реалізує контракт board.h без заліза: рейки з часом наростання, PGOOD із
 * порогом, ключ периферії з керованим dV/dt і просіданням входу від кидка
 * зарядного струму. Дозволяє програти аварії, які на живій платі відтворюють
 * лабораторним джерелом і паяльником. */
#ifndef BOARD_SIM_H
#define BOARD_SIM_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    const char *name;
    bool core_rail_dead;         /* I ступінь не піднімається (немає PGOOD) */
    bool io_rail_dead;           /* LDO DVDD не піднімається */
    uint16_t periph_inrush_mv;   /* просідання входу під час заряду C_load */
    uint32_t overcurrent_at_ms;  /* коли смикнути лінію аварії ключа; 0 — ніколи */
    uint32_t vin_collapse_at_ms; /* коли обвалити вхідну шину; 0 — ніколи */
} sim_scenario_t;

void sim_load(const sim_scenario_t *scenario);
void sim_advance(uint32_t ms);
uint32_t sim_now_ms(void);

/* Скільки мілісекунд піни шини стояли активними при знеструмленій периферії —
 * саме той струм витоку через підтяжки, від якого захищає ізоляція. */
uint32_t sim_leak_ms(void);

#endif /* BOARD_SIM_H */

#ifndef ENERGY_LEDGER_H
#define ENERGY_LEDGER_H

/*
 * Інтегральний облік заряду за фазами циклу.
 *
 * Пристрій не споживає «середній струм»: він спить, прокидається, опитує
 * сенсори й на частку секунди відкриває передавач. Книга витрат накопичує
 * заряд кожної фази окремо, тому одразу видно, що передавач працював менше
 * відсотка часу, а з'їв майже весь бюджет.
 */

#include "budget_types.h"

typedef enum {
    ENERGY_PHASE_SLEEP = 0,
    ENERGY_PHASE_SENSE,
    ENERGY_PHASE_PROCESS,
    ENERGY_PHASE_TX,
    ENERGY_PHASE_COUNT
} energy_phase_t;

typedef struct {
    uint32_t phase_current_ua[ENERGY_PHASE_COUNT];   /* профіль струму фаз */
    uint64_t phase_time_us[ENERGY_PHASE_COUNT];
    uint64_t phase_charge_ua_us[ENERGY_PHASE_COUNT]; /* мкА·мкс */
    uint64_t total_time_us;
    uint64_t total_charge_ua_us;

    energy_phase_t active;
    uint64_t       phase_started_us;
    bool           running;
} energy_ledger_t;

bool energy_ledger_init(energy_ledger_t *ledger,
                        const uint32_t current_ua[ENERGY_PHASE_COUNT]);

/* Дописує вже виміряний відрізок фази (розрахунковий режим). */
bool energy_ledger_account(energy_ledger_t *ledger, energy_phase_t phase,
                           uint64_t duration_us);

/*
 * Перемикання фаз у реальному часі: закриває попередню фазу за годинником
 * аудиту й відкриває нову. Викликається з тих самих місць, де прошивка
 * вмикає периферію.
 */
bool energy_ledger_enter(energy_ledger_t *ledger, energy_phase_t phase);
void energy_ledger_stop(energy_ledger_t *ledger);

uint32_t energy_ledger_avg_current_ua(const energy_ledger_t *ledger);
uint32_t energy_ledger_charge_uah(const energy_ledger_t *ledger);
uint32_t energy_ledger_share_pm(const energy_ledger_t *ledger,
                                energy_phase_t phase);
uint32_t energy_ledger_time_share_pm(const energy_ledger_t *ledger,
                                     energy_phase_t phase);

/* Прогноз ресурсу батареї в годинах за накопиченим середнім струмом. */
uint32_t energy_ledger_life_hours(const energy_ledger_t *ledger,
                                  uint32_t battery_mah);

budget_flags_t energy_ledger_audit(const energy_ledger_t *ledger,
                                   uint32_t battery_mah,
                                   uint32_t required_hours);

const char *energy_phase_name(energy_phase_t phase);

#endif /* ENERGY_LEDGER_H */

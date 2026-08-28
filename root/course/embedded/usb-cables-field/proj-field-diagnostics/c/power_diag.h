// power_diag.h — польовий діагност живлення USB для прошивки.
// Голе залізо: без malloc, фіксований розмір, без блокувань.
#ifndef POWER_DIAG_H
#define POWER_DIAG_H

#include <stdint.h>
#include <stdbool.h>

// Діагноз стану живлення — п'ять клітинок матриці напруга×струм.
typedef enum {
    PWR_OK = 0,       // напруга тримається, струм є — усе гаразд
    PWR_CABLE_DROP,   // напруга просіла ПІД струмом — кабель/контакт
    PWR_NEGOTIATION,  // напруга є, а струму нема — не домовилися (лінії/профіль)
    PWR_SOFT_SOURCE,  // і просадка, і кволий струм — м'який блок
    PWR_NO_POWER      // напруги майже нема — контакт/цілість кабелю
} pwr_diag_t;

// Незмінна конфігурація — заповнюється раз під конкретний виріб.
typedef struct {
    uint16_t vbus_nominal_mv;  // очікувана напруга контракту (напр. 5000)
    uint16_t vbus_sag_mv;      // нижче цього вважаємо ПРОСАДКОЮ (напр. 4400)
    uint16_t vbus_dead_mv;     // нижче цього — живлення практично нема (напр. 3000)
    uint16_t i_expect_ma;      // скільки струму ми домовилися тягти
    uint16_t i_load_min_ma;    // менший струм — це «холостий хід», НЕ міряти
    uint16_t brownout_trip_mv; // нижче — стишуємось (напр. 4000)
    uint16_t brownout_clear_mv;// вище — вертаємось у повний режим (напр. 4300)
    uint8_t  adc_avg_log2;     // усереднення: беремо 2^adc_avg_log2 відліків
    uint8_t  debounce_cycles;  // діагноз має вистоятися стільки циклів
} pwr_cfg_t;

// Робочий стан — нуль на старті означає безпечний холодний старт.
typedef struct {
    const pwr_cfg_t *cfg;     // вказівник на конфіг (у ПЗП — не копіюємо)
    pwr_diag_t diag;          // ПРИЙНЯТИЙ (стабільний) діагноз
    pwr_diag_t pending;       // діагноз-кандидат, що ще дебаунситься
    uint8_t    pending_run;   // скільки циклів кандидат тримається поспіль
    bool       low_power;     // режим стишення (гістерезис brownout)
    uint16_t   vbus_mv;       // останнє усереднене VBUS (для лога/UI)
    uint16_t   i_charge_ma;   // остання оцінка струму
    bool       valid;         // чи був хоч один вимір під навантаженням
} pwr_diag_ctx_t;

// API.
void       pwr_diag_init(pwr_diag_ctx_t *c, const pwr_cfg_t *cfg);
pwr_diag_t pwr_diag_step(pwr_diag_ctx_t *c);         // один цикл нагляду
bool       pwr_low_power(const pwr_diag_ctx_t *c);   // стишити навантаження?
const char *pwr_diag_message(const pwr_diag_ctx_t *c); // чесне слово людині

#endif

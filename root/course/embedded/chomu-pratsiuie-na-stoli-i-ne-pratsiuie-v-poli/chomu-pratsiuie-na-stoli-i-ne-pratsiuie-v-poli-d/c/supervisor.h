/* supervisor.h — політика виживання в полі.
 *
 * Один автомат тримає три незалежні загрози: перегрів, мороз і просадку
 * шини під імпульсом передавача. Кожен перехід має гістерезис — інакше
 * рівно на межі прилад почне клацати навантаженням щоцикла, а клацання
 * реле чи ключа тут дорожче за сам перегрів.
 */
#ifndef SUPERVISOR_H
#define SUPERVISOR_H

#include <stdbool.h>
#include <stdint.h>

/* Пороги з паспорта виробу, не з голови: +85 °C — верхня межа промислового
 * діапазону, 3.0 В — поріг, за яким акумулятор вважається розрядженим. */
#define SUP_TEMP_THROTTLE_ON_C 80
#define SUP_TEMP_THROTTLE_OFF_C 65
#define SUP_TEMP_CRITICAL_C 95
#define SUP_TEMP_CRITICAL_OFF_C 85
#define SUP_TEMP_CHARGE_BLOCK_C 0 /* нижче нуля заряд літію заборонено */
#define SUP_TEMP_CHARGE_ALLOW_C 3
#define SUP_TEMP_HEATER_ON_C (-10)
#define SUP_TEMP_HEATER_OFF_C 0

#define SUP_VOLT_SHED_MV 3100u  /* нижче — скидаємо навантаження */
#define SUP_VOLT_OK_MV 3300u    /* вище — дозволяємо назад */
#define SUP_VOLT_FLOOR_MV 3050u /* прогнозована просадка нижче цього — радіо не вмикаємо */

#define SUP_RADIO_PULSE_MA 2000u /* паспортний імпульс передавача */
#define SUP_BLIND_LIMIT_MS 5000u /* скільки терпимо мовчання давачів */

typedef struct {
    int16_t temp_c;
    bool temp_valid;
    uint16_t vbat_mv;
    bool volt_valid;
} field_sample_t;

typedef enum {
    SUP_THERMAL_NOMINAL = 0,
    SUP_THERMAL_THROTTLED, /* частота ядра поділена, радіо заборонене */
    SUP_THERMAL_CRITICAL   /* усе, крім вимірювання, вимкнено */
} sup_thermal_t;

typedef enum {
    SUP_RADIO_ALLOWED = 0,
    SUP_RADIO_DENIED_HOT,
    SUP_RADIO_DENIED_COLD,
    SUP_RADIO_DENIED_SAG,  /* прогноз просадки нижче підлоги */
    SUP_RADIO_DENIED_BLIND /* невідомо, у якому ми середовищі */
} sup_radio_verdict_t;

typedef struct {
    sup_thermal_t thermal;
    bool charge_blocked;
    bool heater_on;
    bool blind;
    uint32_t blind_since_ms;

    uint16_t idle_mv;    /* напруга без навантаження, остання відома */
    uint16_t r_int_mohm; /* оцінка внутрішнього опору джерела */
    bool r_int_known;

    uint32_t sag_events;
    int16_t last_temp_c;
    uint32_t started_ms;
} supervisor_t;

/* Один замір середовища: NTC на PA0 і напруга акумулятора на PA1.
 * Повертає false, якщо ЖОДЕН з каналів не дався; часткові дані
 * теж корисні, тому поля мають окремі прапорці справжності. */
bool supervisor_sample(field_sample_t *out);

/* safe_start = true після Brownout або HardFault: піднімаємось одразу
 * зі зниженою частотою й без радіо, доки не побачимо здорове середовище. */
void supervisor_init(supervisor_t *sup, bool safe_start, uint32_t now_ms);

/* Крок політики. Викликати з фіксованим періодом. */
void supervisor_step(supervisor_t *sup, const field_sample_t *sample, uint32_t now_ms);

/* Радіо вмикається ТІЛЬКИ через цю пару: запит рахує прогнозовану просадку,
 * звільнення заміряє справжню й уточнює оцінку внутрішнього опору. */
sup_radio_verdict_t supervisor_radio_acquire(supervisor_t *sup);
void supervisor_radio_release(supervisor_t *sup);

const char *supervisor_verdict_name(sup_radio_verdict_t verdict);

#endif /* SUPERVISOR_H */

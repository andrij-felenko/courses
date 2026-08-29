#include "cp_monitor.h"

#include "event_queue.h"
#include "hal.h"

/*
 * Смуги напруги додатного півперіоду. Між смугами навмисно лишені мертві зони
 * (наприклад 10 200…10 800 мВ): вимір, що впав у зазор, не належить жодному
 * класу й не скидає лічильник підтвердження, тож деренчання на межі не
 * породжує зливи подій.
 */
#define CP_A_MIN_MV 10800
#define CP_A_MAX_MV 13000
#define CP_B_MIN_MV 7700
#define CP_B_MAX_MV 10200
#define CP_C_MIN_MV 4800
#define CP_C_MAX_MV 7300

/* Від'ємний півперіод мусить сягати приблизно −12 В: його зникнення означає
 * пробитий або відсутній діод у автомобілі — небезпечна несправність. */
#define CP_NEG_MAX_MV (-10000)

/* Дозволене відхилення періоду ШІМ від 1000 мкс (±5 %). */
#define CP_PERIOD_MIN_US 950u
#define CP_PERIOD_MAX_US 1050u

/* Скільки однакових вимірів поспіль підтверджують клас (10 мс × 3 = 30 мс). */
#define CP_DEBOUNCE_SAMPLES 3u

static cp_class_t s_stable;
static cp_class_t s_candidate;
static uint8_t    s_streak;

void cp_monitor_init(void)
{
    s_stable    = CP_UNKNOWN;
    s_candidate = CP_UNKNOWN;
    s_streak    = 0;
}

static cp_class_t classify(int16_t high_mv, int16_t low_mv, uint32_t period_us)
{
    /* Пілот під ШІМ: період поза допуском означає збій генератора або
     * наведення на лінію. Постійні +12 В (клас A) періоду не мають. */
    const bool pwm_running = (period_us != 0u);
    if (pwm_running && (period_us < CP_PERIOD_MIN_US || period_us > CP_PERIOD_MAX_US)) {
        return CP_INVALID;
    }

    if (high_mv >= CP_A_MIN_MV && high_mv <= CP_A_MAX_MV) {
        /* На класі A автомобіля немає, від'ємного півперіоду теж може не бути. */
        return CP_A;
    }

    /* Нижче класу A лінію навантажує автомобіль — тоді діод обов'язковий. */
    if (low_mv > CP_NEG_MAX_MV) {
        return CP_INVALID;
    }

    if (high_mv >= CP_B_MIN_MV && high_mv <= CP_B_MAX_MV) {
        return CP_B;
    }
    if (high_mv >= CP_C_MIN_MV && high_mv <= CP_C_MAX_MV) {
        return CP_C;
    }

    /* Нижче 4,8 В — стан D, вентиляція, або аварія: станція обидва випадки
     * трактує однаково й знеструмлює лінію. Вище 13 В — пробій із мережі. */
    if (high_mv < CP_C_MIN_MV || high_mv > CP_A_MAX_MV) {
        return CP_INVALID;
    }

    return CP_UNKNOWN; /* мертва зона між смугами */
}

static uint16_t event_for_class(cp_class_t c)
{
    switch (c) {
        case CP_A: return EVT_CP_STATE_A;
        case CP_B: return EVT_CP_STATE_B;
        case CP_C: return EVT_CP_STATE_C;
        default:   return EVT_CP_INVALID;
    }
}

void cp_monitor_sample(void)
{
    const cp_class_t raw = classify(hal_pilot_read_high_mv(),
                                    hal_pilot_read_low_mv(),
                                    hal_pilot_period_us());

    if (raw == CP_UNKNOWN) {
        return; /* вимір у мертвій зоні: не підтверджує й не спростовує */
    }

    if (raw != s_candidate) {
        s_candidate = raw;
        s_streak    = 1;
        return;
    }

    if (s_streak < CP_DEBOUNCE_SAMPLES) {
        ++s_streak;
    }

    if (s_streak < CP_DEBOUNCE_SAMPLES || raw == s_stable) {
        return;
    }

    /*
     * Аварію не тримаємо під дребезг-фільтром довше за потрібне: три виміри
     * поспіль — це 30 мс, а контактор розмикається за 20 мс, тож повний час
     * до знеструмлення лишається в межах 50 мс.
     */
    s_stable = raw;
    (void)event_queue_push(&g_events, event_for_class(raw), (uint16_t)raw);
}

cp_class_t cp_monitor_class(void)
{
    return s_stable;
}

const char *cp_class_name(cp_class_t c)
{
    switch (c) {
        case CP_A:       return "A (+12 В, кабель від'єднано)";
        case CP_B:       return "B (+9 В, підключено)";
        case CP_C:       return "C (+6 В, запит енергії)";
        case CP_INVALID: return "аварія лінії пілота";
        default:         return "невідомо";
    }
}

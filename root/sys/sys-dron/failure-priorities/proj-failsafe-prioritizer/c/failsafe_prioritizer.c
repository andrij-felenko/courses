/**
 * @file failsafe_prioritizer.c
 * @brief Детермінований пріоритетний арбітр аварійних станів автопілота на C99/C11.
 * Повністю статична пам'ять, нульовий оверхед, гарантований O(N) час обчислення.
 */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define FS_MAX_RULES 16

/* Бітові маски сенсорних та виконавчих спроможностей апарата (Capabilities) */
#define CAP_ATTITUDE_ESTIMATE   (1u << 0)  /* Справний контур просторової орієнтації (IMU/EKF) */
#define CAP_ALTITUDE_ESTIMATE   (1u << 1)  /* Барометрична або далекомірна висота */
#define CAP_POSITION_3D_FIX     (1u << 2)  /* 3D-координати (GNSS / RTK / оптичний потік) */
#define CAP_PROPULSION_CONTROL  (1u << 3)  /* Справні регулятори швидкості (ESC) та мотори */
#define CAP_COMMUNICATION_LINK  (1u << 4)  /* Активний канал телеметрії або RC */

/* Ідентифікатори уніфікованих аварійних дій автопілота */
typedef enum {
    FS_ACTION_NONE = 0,
    FS_ACTION_WARN_ONLY,          /* Запис логу та звукове сповіщення оператора */
    FS_ACTION_ALT_HOLD_DRIFT,     /* Утримання висоти за барометром без контролю горизонтального зносу */
    FS_ACTION_HOLD_POSITION,      /* Зависання в поточній точці за координатами */
    FS_ACTION_RTL,                /* Повернення на точку старту (Return to Launch) */
    FS_ACTION_EMERGENCY_LAND,     /* Вертикальна керована посадка на поточному місці */
    FS_ACTION_DEPLOY_PARACHUTE,   /* Зупинка моторів та викид піротехнічного парашута */
    FS_ACTION_TERMINATE_FLIGHT    /* Миттєве знеструмлення приводів (FTS / Disarm) */
} FailsafeAction_t;

/* Прапорці налаштування правил */
#define RULE_FLAG_NONE   0x00
#define RULE_FLAG_LATCH  0x01  /* Незворотна фіксація: активувавшись, діє до Disarm */

/* Опис статичного правила аварійного реагування */
typedef struct {
    uint8_t          priority;          /* Числовий ранг (0 = найвищий, 255 = найнижчий) */
    uint16_t         required_caps;     /* Маска спроможностей, обов'язкових для desired_action */
    FailsafeAction_t desired_action;    /* Дія за наявності всіх спроможностей */
    FailsafeAction_t fallback_action;   /* Деградована дія за браку сенсорів */
    uint16_t         confirm_delay_ms;  /* Час підтвердження відмови в мілісекундах */
    uint8_t          flags;             /* RULE_FLAG_* */
    const char      *name;              /* Текстова назва для журналювання та телеметрії */
} FailsafeRule_t;

/* Динамічний стан правила в пам'яті */
typedef struct {
    uint16_t timer_ms;  /* Лічильник безперервної активності відмови */
    bool     latched;   /* Ознака незворотної фіксації стану */
} RuleRuntimeState_t;

/* Головна структура контексту пріоритетного арбітра */
typedef struct {
    FailsafeRule_t     rules[FS_MAX_RULES];
    RuleRuntimeState_t states[FS_MAX_RULES];
    size_t             rule_count;
    FailsafeAction_t   current_action;
    uint8_t            current_priority;
    int8_t             active_rule_index;
} FailsafeArbiter_t;

/**
 * @brief Ініціалізація структури арбітра.
 */
void failsafe_arbiter_init(FailsafeArbiter_t *arb) {
    if (!arb) return;
    memset(arb, 0, sizeof(FailsafeArbiter_t));
    arb->current_action = FS_ACTION_NONE;
    arb->current_priority = 255;
    arb->active_rule_index = -1;
}

/**
 * @brief Реєстрація нового правила в таблиці арбітражу.
 */
bool failsafe_arbiter_add_rule(FailsafeArbiter_t *arb, const FailsafeRule_t *rule) {
    if (!arb || !rule || arb->rule_count >= FS_MAX_RULES) {
        return false;
    }
    arb->rules[arb->rule_count] = *rule;
    arb->states[arb->rule_count].timer_ms = 0;
    arb->states[arb->rule_count].latched = false;
    arb->rule_count++;
    return true;
}

/**
 * @brief Головний крок оновлення стану арбітра (викликається в циклі RTOS 50-100 Гц).
 * @param arb Покажчик на контекст арбітра.
 * @param raw_failures_mask Бітова маска сирих відмов (біт i відповідає rules[i]).
 * @param current_caps Бітова маска доступних апаратних спроможностей (CAP_*).
 * @param delta_time_ms Період польотного такту в мілісекундах.
 * @return Результуюча активна безпечна дія.
 */
FailsafeAction_t failsafe_arbiter_update(
    FailsafeArbiter_t *arb,
    uint16_t raw_failures_mask,
    uint16_t current_caps,
    uint16_t delta_time_ms
) {
    if (!arb) return FS_ACTION_NONE;

    uint8_t best_priority = 255;
    FailsafeAction_t best_action = FS_ACTION_NONE;
    int8_t best_rule_idx = -1;

    for (size_t i = 0; i < arb->rule_count; ++i) {
        const FailsafeRule_t *r = &arb->rules[i];
        RuleRuntimeState_t *s = &arb->states[i];
        bool is_active = (raw_failures_mask & (1u << i)) != 0;

        /* Фаза 1: Симетричний інтегратор підтвердження (Debouncing) */
        if (is_active) {
            if (s->timer_ms + delta_time_ms < r->confirm_delay_ms) {
                s->timer_ms += delta_time_ms;
            } else {
                s->timer_ms = r->confirm_delay_ms;
            }
        } else {
            if (!s->latched) {
                if (s->timer_ms > delta_time_ms) {
                    s->timer_ms -= delta_time_ms;
                } else {
                    s->timer_ms = 0;
                }
            }
        }

        /* Фаза 2: Перевірка кваліфікації відмови */
        bool qualified = (s->timer_ms >= r->confirm_delay_ms) || s->latched;
        if (qualified) {
            if (r->flags & RULE_FLAG_LATCH) {
                s->latched = true;
            }

            /* Фаза 3: Порівняння рангів та перевірка сенсорної здійсненності */
            if (r->priority < best_priority) {
                bool caps_ok = (current_caps & r->required_caps) == r->required_caps;
                FailsafeAction_t effective_action = caps_ok ? r->desired_action : r->fallback_action;

                best_priority = r->priority;
                best_action = effective_action;
                best_rule_idx = (int8_t)i;
            }
        }
    }

    /* Фаза 4: Атомарне призначення результуючої дії */
    arb->current_action = best_action;
    arb->current_priority = best_priority;
    arb->active_rule_index = best_rule_idx;

    return arb->current_action;
}

/**
 * @brief Очищення стану фіксації (дозволено лише після повної зупинки на землі).
 */
void failsafe_arbiter_reset_latches(FailsafeArbiter_t *arb) {
    if (!arb) return;
    for (size_t i = 0; i < arb->rule_count; ++i) {
        arb->states[i].latched = false;
        arb->states[i].timer_ms = 0;
    }
    arb->current_action = FS_ACTION_NONE;
    arb->current_priority = 255;
    arb->active_rule_index = -1;
}

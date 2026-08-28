#include <stdint.h>
#include <stdbool.h>

// Коди дій аварійного автомата
typedef enum {
    FS_ACTION_NONE = 0,
    FS_ACTION_WARN,
    FS_ACTION_ALTHOLD,
    FS_ACTION_RTL,
    FS_ACTION_LAND,
    FS_ACTION_TERMINATE
} fs_action_t;

// Конфігураційні таймаути фільтрації несправностей (у мілісекундах)
typedef struct {
    uint32_t rc_timeout_ms;       // Типово 1500 мс
    uint32_t gcs_timeout_ms;      // Типово 5000 мс
    uint32_t gnss_timeout_ms;     // Типово 3000 мс
    uint32_t batt_debounce_ms;    // Типово 1000 мс
    uint32_t geofence_debounce_ms;// Типово 500 мс
} fs_config_t;

// Стан таймерів відмов
typedef struct {
    uint32_t rc_lost_start_ms;
    uint32_t gcs_lost_start_ms;
    uint32_t gnss_fail_start_ms;
    uint32_t batt_low_start_ms;
    uint32_t batt_crit_start_ms;
    uint32_t geofence_start_ms;
    uint32_t confirmed_faults;
    fs_action_t active_action;
} fs_state_t;

static void update_fault_timer(bool condition, uint32_t now_ms,
                               uint32_t *start_time, uint32_t threshold_ms,
                               uint32_t *fault_mask, uint32_t flag)
{
    if (condition) {
        if (*start_time == 0) {
            *start_time = now_ms; // Фіксація початку аномалії
        }
        if ((now_ms - *start_time) >= threshold_ms) {
            *fault_mask |= flag;  // Підтвердження стійкої відмови
        }
    } else {
        *start_time = 0;
        *fault_mask &= ~flag;     // Скидання при відновленні норми
    }
}

fs_action_t fs_arbiter_update(const fs_config_t *cfg, fs_state_t *st,
                              uint32_t raw_fault_flags, uint32_t now_ms)
{
    // 1. Оновлення та підтвердження таймерів для кожного типу збою
    update_fault_timer((raw_fault_flags & (1u << 0)) != 0, now_ms,
                       &st->rc_lost_start_ms, cfg->rc_timeout_ms,
                       &st->confirmed_faults, (1u << 0));

    update_fault_timer((raw_fault_flags & (1u << 1)) != 0, now_ms,
                       &st->gcs_lost_start_ms, cfg->gcs_timeout_ms,
                       &st->confirmed_faults, (1u << 1));

    update_fault_timer((raw_fault_flags & (1u << 2)) != 0, now_ms,
                       &st->gnss_fail_start_ms, cfg->gnss_timeout_ms,
                       &st->confirmed_faults, (1u << 2));

    update_fault_timer((raw_fault_flags & (1u << 3)) != 0, now_ms,
                       &st->batt_low_start_ms, cfg->batt_debounce_ms,
                       &st->confirmed_faults, (1u << 3));

    update_fault_timer((raw_fault_flags & (1u << 4)) != 0, now_ms,
                       &st->batt_crit_start_ms, cfg->batt_debounce_ms,
                       &st->confirmed_faults, (1u << 4));

    update_fault_timer((raw_fault_flags & (1u << 5)) != 0, now_ms,
                       &st->geofence_start_ms, cfg->geofence_debounce_ms,
                       &st->confirmed_faults, (1u << 5));

    // Апаратна відмова приводу або втрата орієнтації фіксується негайно
    if (raw_fault_flags & (1u << 6)) st->confirmed_faults |= (1u << 6);
    if (raw_fault_flags & (1u << 7)) st->confirmed_faults |= (1u << 7);

    uint32_t f = st->confirmed_faults;

    // 2. Дерево арбітражу пріоритетів (від найкритичнішого до м'якого)

    // Пріоритет 1: Катастрофічна втрата орієнтації
    if (f & (1u << 7)) {
        st->active_action = FS_ACTION_TERMINATE;
        return st->active_action;
    }

    // Пріоритет 2: Критичний розряд батареї
    if (f & (1u << 4)) {
        // Енергії на повернення немає: тільки негайна посадка на місці
        st->active_action = FS_ACTION_LAND;
        return st->active_action;
    }

    // Пріоритет 3: Порушення геозони
    if (f & (1u << 5)) {
        // Якщо GNSS працює, повертаємося додому або сідаємо на межі
        if (!(f & (1u << 2))) {
            st->active_action = FS_ACTION_RTL;
        } else {
            st->active_action = FS_ACTION_LAND;
        }
        return st->active_action;
    }

    // Пріоритет 4: Втрата зв'язку керування (RC Lost)
    if (f & (1u << 0)) {
        // Є супутники — безпечне повернення
        if (!(f & (1u << 2))) {
            st->active_action = FS_ACTION_RTL;
        } else {
            // Без супутників RTL неможливий — перехід на спуск або AltHold
            st->active_action = FS_ACTION_LAND;
        }
        return st->active_action;
    }

    // Пріоритет 5: Одиночна втрата GNSS при наявному зв'язку
    if (f & (1u << 2)) {
        // Залишаємося в утриманні висоти для передачі ручного контролю
        st->active_action = FS_ACTION_ALTHOLD;
        return st->active_action;
    }

    // Пріоритет 6: Попереджувальний поріг батареї
    if (f & (1u << 3)) {
        st->active_action = (!(f & (1u << 2))) ? FS_ACTION_RTL : FS_ACTION_LAND;
        return st->active_action;
    }

    st->active_action = FS_ACTION_NONE;
    return st->active_action;
}

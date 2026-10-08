#include "ss41f_hall.h"
#include <stddef.h>

/**
 * @brief Таблиця відповідності 3-бітового коду (0..7) сектору ротора (1..6).
 * 
 * Біти коду: Bit 2 = Hall A, Bit 1 = Hall B, Bit 0 = Hall C.
 * Індекси 0 (000) та 7 (111) відповідають забороненим апаратним станам.
 */
const hall_sector_t hall_lut[8] = {
    [0] = HALL_SECTOR_INVALID, /* 000: Заборонений стан (обрив VCC/GND/сигналів) */
    [1] = HALL_SECTOR_1,       /* 001: Сектор 1 */
    [2] = HALL_SECTOR_3,       /* 010: Сектор 3 */
    [3] = HALL_SECTOR_2,       /* 011: Сектор 2 */
    [4] = HALL_SECTOR_5,       /* 100: Сектор 5 */
    [5] = HALL_SECTOR_6,       /* 101: Сектор 6 */
    [6] = HALL_SECTOR_4,       /* 110: Сектор 4 */
    [7] = HALL_SECTOR_INVALID  /* 111: Заборонений стан (коротке на VCC або обрив з pull-up) */
};

/* Внутрішній стан телеметрії драйвера */
static volatile hall_telemetry_t g_telemetry = {
    .raw_code = 0,
    .current_sector = HALL_SECTOR_INVALID,
    .previous_sector = HALL_SECTOR_INVALID,
    .direction = HALL_DIR_UNKNOWN,
    .transition_count = 0,
    .error_count = 0,
    .last_error = HALL_ERR_NONE
};

/* Зареєстровані зворотні виклики */
static hall_sector_change_cb_t g_sector_cb = NULL;
static hall_error_cb_t         g_error_cb  = NULL;

void hall_init(void) {
    g_telemetry.raw_code = 0;
    g_telemetry.current_sector = HALL_SECTOR_INVALID;
    g_telemetry.previous_sector = HALL_SECTOR_INVALID;
    g_telemetry.direction = HALL_DIR_UNKNOWN;
    g_telemetry.transition_count = 0;
    g_telemetry.error_count = 0;
    g_telemetry.last_error = HALL_ERR_NONE;

    g_sector_cb = NULL;
    g_error_cb = NULL;
}

hall_sector_t hall_decode_code(uint8_t raw_code) {
    if (raw_code > 7U) {
        return HALL_SECTOR_INVALID;
    }
    return hall_lut[raw_code & 0x07U];
}

bool hall_is_valid_transition(hall_sector_t prev, hall_sector_t curr) {
    /* Перехід з невизначеного початкового стану дозволений до будь-якого валідного сектора */
    if (prev == HALL_SECTOR_INVALID) {
        return (curr >= HALL_SECTOR_1 && curr <= HALL_SECTOR_6);
    }

    if (curr == HALL_SECTOR_INVALID) {
        return false;
    }

    /* Перевірка руху CW (наступний сектор) */
    hall_sector_t expected_cw = (hall_sector_t)((prev % 6) + 1);
    if (curr == expected_cw) {
        return true;
    }

    /* Перевірка руху CCW (попередній сектор) */
    hall_sector_t expected_ccw = (prev == HALL_SECTOR_1) ? HALL_SECTOR_6 : (hall_sector_t)(prev - 1);
    if (curr == expected_ccw) {
        return true;
    }

    return false;
}

hall_error_t hall_process_state(uint8_t raw_code) {
    raw_code &= 0x07U;
    g_telemetry.raw_code = raw_code;

    /* 1. Перевірка на заборонені кодові комбінації (000 та 111) */
    if (raw_code == HALL_CODE_INVALID_LOW) {
        g_telemetry.last_error = HALL_ERR_INVALID_CODE_000;
        g_telemetry.error_count++;
        if (g_error_cb != NULL) {
            g_error_cb(HALL_ERR_INVALID_CODE_000, raw_code);
        }
        return HALL_ERR_INVALID_CODE_000;
    }

    if (raw_code == HALL_CODE_INVALID_HIGH) {
        g_telemetry.last_error = HALL_ERR_INVALID_CODE_111;
        g_telemetry.error_count++;
        if (g_error_cb != NULL) {
            g_error_cb(HALL_ERR_INVALID_CODE_111, raw_code);
        }
        return HALL_ERR_INVALID_CODE_111;
    }

    /* 2. Декодування електричного сектора за LUT */
    hall_sector_t new_sector = hall_decode_code(raw_code);
    hall_sector_t old_sector = g_telemetry.current_sector;

    /* 3. Перевірка коректності фазового переходу */
    if (!hall_is_valid_transition(old_sector, new_sector)) {
        g_telemetry.last_error = HALL_ERR_ILLEGAL_TRANSITION;
        g_telemetry.error_count++;
        if (g_error_cb != NULL) {
            g_error_cb(HALL_ERR_ILLEGAL_TRANSITION, raw_code);
        }
        return HALL_ERR_ILLEGAL_TRANSITION;
    }

    /* 4. Визначення напрямку обертання */
    if (old_sector != HALL_SECTOR_INVALID && old_sector != new_sector) {
        hall_sector_t expected_cw = (hall_sector_t)((old_sector % 6) + 1);
        if (new_sector == expected_cw) {
            g_telemetry.direction = HALL_DIR_CW;
        } else {
            g_telemetry.direction = HALL_DIR_CCW;
        }
    }

    /* 5. Оновлення стану телеметрії */
    g_telemetry.previous_sector = old_sector;
    g_telemetry.current_sector = new_sector;
    g_telemetry.transition_count++;
    g_telemetry.last_error = HALL_ERR_NONE;

    /* 6. Виклик callback-функції при зміні сектора */
    if (g_sector_cb != NULL && old_sector != new_sector) {
        g_sector_cb(new_sector, old_sector, raw_code);
    }

    return HALL_ERR_NONE;
}

void hall_register_sector_callback(hall_sector_change_cb_t cb) {
    g_sector_cb = cb;
}

void hall_register_error_callback(hall_error_cb_t cb) {
    g_error_cb = cb;
}

void hall_get_telemetry(hall_telemetry_t *telemetry) {
    if (telemetry != NULL) {
        telemetry->raw_code         = g_telemetry.raw_code;
        telemetry->current_sector   = g_telemetry.current_sector;
        telemetry->previous_sector  = g_telemetry.previous_sector;
        telemetry->direction        = g_telemetry.direction;
        telemetry->transition_count = g_telemetry.transition_count;
        telemetry->error_count      = g_telemetry.error_count;
        telemetry->last_error       = g_telemetry.last_error;
    }
}

void hall_reset_telemetry(void) {
    g_telemetry.transition_count = 0;
    g_telemetry.error_count = 0;
    g_telemetry.last_error = HALL_ERR_NONE;
}

#include "climate_core.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

/**
 * @file climate_core.c
 * @brief Реалізація чистої бізнес-логіки прикладного ядра мікроклімату.
 */

const char *core_status_to_string(core_status_t status) {
    switch (status) {
        case CORE_STATUS_OK:
            return "CORE_STATUS_OK";
        case CORE_STATUS_INVALID_ARG:
            return "CORE_STATUS_INVALID_ARG";
        case CORE_STATUS_UNAUTHORIZED:
            return "CORE_STATUS_UNAUTHORIZED";
        case CORE_STATUS_OUT_OF_RANGE:
            return "CORE_STATUS_OUT_OF_RANGE";
        case CORE_STATUS_INTERNAL_ERROR:
            return "CORE_STATUS_INTERNAL_ERROR";
        default:
            return "CORE_STATUS_UNKNOWN";
    }
}

void climate_core_init(climate_core_t *core, const char *valid_auth_token) {
    if (!core) {
        return;
    }
    memset(core, 0, sizeof(*core));

    if (valid_auth_token) {
        strncpy(core->expected_auth_token, valid_auth_token, sizeof(core->expected_auth_token) - 1);
    }

    core->port.ctx = core;
    core->port.execute = climate_core_execute;
    core->room_count = 0;
}

inbound_port_t *climate_core_get_port(climate_core_t *core) {
    if (!core) {
        return NULL;
    }
    return &core->port;
}

core_status_t climate_core_execute(inbound_port_t *self, const climate_cmd_t *cmd, climate_result_t *out_result) {
    if (!self || !self->ctx || !cmd || !out_result) {
        if (out_result) {
            out_result->status = CORE_STATUS_INVALID_ARG;
            snprintf(out_result->message, sizeof(out_result->message), "Неприпустимі покажчики аргументів виклику порту");
        }
        return CORE_STATUS_INVALID_ARG;
    }

    climate_core_t *core = (climate_core_t *)self->ctx;
    memset(out_result, 0, sizeof(*out_result));

    /* 1. Доменна валідація ідентифікатора кімнати */
    if (cmd->room_id[0] == '\0') {
        out_result->status = CORE_STATUS_INVALID_ARG;
        snprintf(out_result->message, sizeof(out_result->message), "Ідентифікатор кімнати не може бути порожнім");
        return CORE_STATUS_INVALID_ARG;
    }

    /* 2. Доменна перевірка автентифікації */
    if (strcmp(cmd->auth_token, core->expected_auth_token) != 0) {
        out_result->status = CORE_STATUS_UNAUTHORIZED;
        snprintf(out_result->message, sizeof(out_result->message), "Помилка автентифікації: недійсний токен доступу");
        return CORE_STATUS_UNAUTHORIZED;
    }

    /* 3. Бізнес-правило: безпечний температурний діапазон */
    if (isnan(cmd->target_temp_c) ||
        cmd->target_temp_c < CLIMATE_TEMP_MIN_C ||
        cmd->target_temp_c > CLIMATE_TEMP_MAX_C) {
        out_result->status = CORE_STATUS_OUT_OF_RANGE;
        snprintf(out_result->message, sizeof(out_result->message),
                 "Цільова температура %.2f C виходить за межі допустимого діапазону [%.1f; %.1f] C",
                 cmd->target_temp_c, CLIMATE_TEMP_MIN_C, CLIMATE_TEMP_MAX_C);
        return CORE_STATUS_OUT_OF_RANGE;
    }

    /* 4. Пошук існуючої кімнати або реєстрація нової */
    double previous_temp = CLIMATE_DEFAULT_TEMP_C;
    int target_idx = -1;

    for (size_t i = 0; i < core->room_count; i++) {
        if (core->rooms[i].is_occupied && strcmp(core->rooms[i].room_id, cmd->room_id) == 0) {
            target_idx = (int)i;
            previous_temp = core->rooms[i].current_temp_c;
            break;
        }
    }

    if (target_idx < 0) {
        if (core->room_count >= CLIMATE_CORE_MAX_ROOMS) {
            out_result->status = CORE_STATUS_INTERNAL_ERROR;
            snprintf(out_result->message, sizeof(out_result->message),
                     "Переповнення внутрішнього реєстру кімнат ядра (ліміт %d)", CLIMATE_CORE_MAX_ROOMS);
            return CORE_STATUS_INTERNAL_ERROR;
        }
        target_idx = (int)core->room_count;
        strncpy(core->rooms[target_idx].room_id, cmd->room_id, sizeof(core->rooms[target_idx].room_id) - 1);
        core->rooms[target_idx].is_occupied = true;
        core->room_count++;
        previous_temp = CLIMATE_DEFAULT_TEMP_C;
    }

    /* 5. Оновлення стану кімнати */
    core->rooms[target_idx].current_temp_c = cmd->target_temp_c;

    out_result->status = CORE_STATUS_OK;
    out_result->previous_temp_c = previous_temp;
    out_result->current_temp_c = cmd->target_temp_c;
    snprintf(out_result->message, sizeof(out_result->message),
             "Кімната '%s': температуру успішно змінено з %.2f C на %.2f C",
             cmd->room_id, previous_temp, cmd->target_temp_c);

    return CORE_STATUS_OK;
}

bool climate_core_get_room_temp(const climate_core_t *core, const char *room_id, double *out_temp) {
    if (!core || !room_id || !out_temp) {
        return false;
    }
    for (size_t i = 0; i < core->room_count; i++) {
        if (core->rooms[i].is_occupied && strcmp(core->rooms[i].room_id, room_id) == 0) {
            *out_temp = core->rooms[i].current_temp_c;
            return true;
        }
    }
    return false;
}

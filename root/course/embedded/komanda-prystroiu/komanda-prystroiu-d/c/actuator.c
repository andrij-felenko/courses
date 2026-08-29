#include "actuator.h"
#include "platform.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    act_status_t status;
    uint8_t      job_type;

    /* спільне для тривалих операцій */
    uint32_t start_ms;
    int32_t  start_pos;
    int32_t  target_pos;
    int32_t  goal_amount;   /* мілілітри для насоса */

    /* стан заліза */
    int32_t  position;
    uint8_t  relay[2];
    bool     supply_ok;
    int32_t  stall_at;

    /* латч термінального результату */
    int32_t  result_detail;
    int32_t  result_error;
} actuator_t;

static actuator_t g_act;

void actuator_init(void) {
    memset(&g_act, 0, sizeof(g_act));
    g_act.status    = ACT_IDLE;
    g_act.supply_ok = true;
    g_act.stall_at  = INT32_MIN;
    g_act.position  = 0;
}

int32_t actuator_position(void) {
    return g_act.position;
}

void actuator_set_supply_ok(bool ok) {
    g_act.supply_ok = ok;
    printf("      [залізо] шина живлення приводів: %s\n", ok ? "у нормі" : "просіла");
}

void actuator_set_stall_at(int32_t position) {
    g_act.stall_at = position;
    if (position != INT32_MIN) {
        printf("      [залізо] механічна перешкода на позиції %ld\n", (long)position);
    }
}

static void finish_ok(int32_t detail) {
    g_act.status        = ACT_DONE;
    g_act.result_detail = detail;
    g_act.result_error  = E_OK;
}

static void finish_fail(int32_t err, int32_t detail) {
    g_act.status        = ACT_FAILED;
    g_act.result_detail = detail;
    g_act.result_error  = err;
}

cmd_err_t actuator_start(uint8_t type, const uint8_t *payload, uint8_t len) {
    if (g_act.status == ACT_BUSY) return E_UNKNOWN_TYPE;   /* диспетчер такого не допускає */

    g_act.job_type = type;
    g_act.start_ms = plat_now_ms();

    switch (type) {
        case CMD_NOOP:
            finish_ok(0);
            return E_OK;

        case CMD_SET_RELAY: {
            if (len < 2) return E_BAD_PAYLOAD;
            uint8_t ch = payload[0];
            uint8_t on = payload[1] ? 1u : 0u;
            if (ch >= 2) return E_BAD_PAYLOAD;
            /* Перед подачею струму на котушку перевіряємо шину живлення:
             * замкнути ключ при просілій напрузі — це залипле реле й скид МК. */
            if (!g_act.supply_ok) return E_SUPPLY_SAG;

            g_act.relay[ch] = on;   /* тут був би gpio_set_level(RELAY_PIN[ch], on) */
            printf("      [залізо] реле %u -> %s\n", (unsigned)ch, on ? "ON" : "OFF");
            finish_ok(on);
            return E_OK;
        }

        case CMD_GOTO_POS: {
            if (len < 4) return E_BAD_PAYLOAD;
            int32_t target = wire_get_i32(payload);
            if (!g_act.supply_ok) return E_SUPPLY_SAG;

            g_act.start_pos  = g_act.position;
            g_act.target_pos = target;
            if (target == g_act.position) {
                /* Абсолютна команда на вже досягнуту позицію: рухатись нікуди,
                 * але команда все одно успішна — у цьому й сенс ідемпотентності. */
                finish_ok(g_act.position);
                return E_OK;
            }
            g_act.status = ACT_BUSY;
            printf("      [залізо] каретка %ld -> %ld (%d кроків/с)\n",
                   (long)g_act.position, (long)target, ACT_STEP_RATE_HZ);
            return E_OK;
        }

        case CMD_DISPENSE_ML: {
            if (len < 2) return E_BAD_PAYLOAD;
            int32_t ml = (int32_t)wire_get_u16(payload);
            if (ml <= 0) return E_BAD_PAYLOAD;
            if (!g_act.supply_ok) return E_SUPPLY_SAG;

            g_act.goal_amount = ml;
            g_act.status      = ACT_BUSY;
            printf("      [залізо] насос: наливаємо %ld мл\n", (long)ml);
            return E_OK;
        }

        case CMD_CALIBRATE:
            g_act.status = ACT_BUSY;
            printf("      [залізо] калібрування АЦП (%d мс)\n", ACT_CALIBRATE_MS);
            return E_OK;

        default:
            return E_UNKNOWN_TYPE;
    }
}

/* Просування кроків: скільки їх належить зробити за час, що минув. */
static void advance_stepper(uint32_t elapsed_ms) {
    int64_t steps = ((int64_t)elapsed_ms * ACT_STEP_RATE_HZ) / 1000;
    int32_t dir   = (g_act.target_pos >= g_act.start_pos) ? 1 : -1;
    int64_t moved = (int64_t)g_act.start_pos + dir * steps;

    int32_t pos;
    if (dir > 0) pos = (moved > g_act.target_pos) ? g_act.target_pos : (int32_t)moved;
    else         pos = (moved < g_act.target_pos) ? g_act.target_pos : (int32_t)moved;

    /* Струмовий захист: перешкода на шляху зупиняє вал раніше цілі. */
    if (g_act.stall_at != INT32_MIN) {
        bool crossed = (dir > 0) ? (pos >= g_act.stall_at && g_act.start_pos < g_act.stall_at)
                                 : (pos <= g_act.stall_at && g_act.start_pos > g_act.stall_at);
        if (crossed) {
            g_act.position = g_act.stall_at;
            printf("      [залізо] СТРУМОВИЙ ЗАХИСТ: вал став на %ld\n", (long)g_act.stall_at);
            finish_fail(E_STALL, g_act.position);
            return;
        }
    }

    g_act.position = pos;
    if (pos == g_act.target_pos) finish_ok(pos);
}

act_result_t actuator_poll(void) {
    act_result_t out = { ACT_IDLE, 0, E_OK };

    if (g_act.status == ACT_BUSY) {
        uint32_t elapsed = plat_now_ms() - g_act.start_ms;

        switch (g_act.job_type) {
            case CMD_GOTO_POS:
                advance_stepper(elapsed);
                break;

            case CMD_DISPENSE_ML: {
                int32_t need_ms = g_act.goal_amount * ACT_DISPENSE_MS_ML;
                if (!g_act.supply_ok) {
                    /* Напруга просіла посеред наливання — насос став. */
                    int32_t poured = (int32_t)(elapsed / ACT_DISPENSE_MS_ML);
                    finish_fail(E_SUPPLY_SAG, poured);
                } else if ((int32_t)elapsed >= need_ms) {
                    finish_ok(g_act.goal_amount);
                }
                break;
            }

            case CMD_CALIBRATE:
                if (elapsed >= (uint32_t)ACT_CALIBRATE_MS) finish_ok(37);   /* зміряний зсув нуля */
                break;

            default:
                finish_ok(0);
                break;
        }
    }

    if (g_act.status == ACT_DONE || g_act.status == ACT_FAILED) {
        out.status = g_act.status;
        out.detail = g_act.result_detail;
        out.error  = g_act.result_error;
        g_act.status = ACT_IDLE;      /* термінальний результат віддається один раз */
        return out;
    }

    out.status = g_act.status;
    out.detail = g_act.position;
    return out;
}

void actuator_abort(void) {
    if (g_act.status == ACT_BUSY) {
        printf("      [залізо] АВАРІЙНА ЗУПИНКА: струм із драйвера знято на позиції %ld\n",
               (long)g_act.position);
    }
    g_act.status = ACT_IDLE;
}

void actuator_home(void) {
    printf("      [залізо] гомінг: механізм зводиться в нульову точку з %ld\n",
           (long)g_act.position);
    g_act.position = 0;
    g_act.relay[0] = 0;
    g_act.relay[1] = 0;
    g_act.status   = ACT_IDLE;
}

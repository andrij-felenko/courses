/* Прошивка вузла: мережевий колбек, швидкий цикл і стенд замість заліза.
   Збірка: cc -std=c11 -Wall -Wextra *.c -o fw */

#include "actuator.h"
#include "dedup.h"
#include "link.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

/* --- Стенд: вал, кінцевики, драйвер і годинник -------------------------- */

#define TICK_MS 10u
#define STEP_MS 25u   /* один відсоток ходу за 25 мс */

static uint32_t g_now_ms;
static uint32_t g_epoch_sec = 1725000000u;
static uint32_t g_epoch_carry_ms;
static uint32_t g_step_carry_ms;
static int      g_position_pct;
static int      g_drive_target = -1;   /* -1 — привід знеструмлений */
static bool     g_jammed;

uint32_t hal_millis(void)        { return g_now_ms; }
uint32_t hal_epoch_sec(void)     { return g_epoch_sec; }
int      hal_position_pct(void)  { return g_position_pct; }
bool     hal_limit_closed(void)  { return g_position_pct <= 0; }
bool     hal_limit_open(void)    { return g_position_pct >= 100; }
void     hal_drive_set(int t)    { g_drive_target = t; }
void     hal_drive_stop(void)    { g_drive_target = -1; }

static void board_tick(void)
{
    g_now_ms += TICK_MS;
    g_epoch_carry_ms += TICK_MS;
    while (g_epoch_carry_ms >= 1000u) {
        g_epoch_carry_ms -= 1000u;
        ++g_epoch_sec;
    }

    if (g_drive_target < 0 || g_jammed) {
        g_step_carry_ms = 0;
        return;
    }
    g_step_carry_ms += TICK_MS;
    while (g_step_carry_ms >= STEP_MS) {
        g_step_carry_ms -= STEP_MS;
        if (g_position_pct < g_drive_target) {
            ++g_position_pct;
        } else if (g_position_pct > g_drive_target) {
            --g_position_pct;
        } else {
            break;
        }
    }
}

/* Швидкий цикл loop(): жодних затримок, лише опитування воркера. */
static void run_for(uint32_t ms)
{
    for (uint32_t t = 0; t < ms; t += TICK_MS) {
        board_tick();
        actuator_poll(g_now_ms);
    }
}

/* --- Мережевий колбек ---------------------------------------------------- */

void handle_incoming_downlink(const char *payload)
{
    downlink_cmd_t cmd;
    link_parse_t rc;
    uint32_t now_sec;
    const dedup_entry_t *seen;
    act_job_t job;

    rc = link_parse_downlink(payload, &cmd);
    if (rc != LINK_PARSE_OK) {
        link_publish_nack(link_parse_reason(rc));
        return;
    }

    now_sec = hal_epoch_sec();
    if (now_sec > cmd.issued_at_sec + cmd.ttl_sec) {
        /* Наказ пролежав у черзі довше, ніж дозволив оператор: виконувати
           його наосліп небезпечно — за цей час стан установки міг змінитися. */
        link_publish_status(cmd.cmd_id, "EXPIRED", 0, actuator_position(), ERR_TTL_EXPIRED);
        return;
    }

    seen = dedup_find(cmd.cmd_id);
    if (seen != NULL) {
        /* Повтор після втраченої квитанції: реле не смикаємо, віддаємо
           останній відомий стан заліза. */
        link_publish_ack(cmd.cmd_id, "ACK_DUPLICATE");
        link_publish_status(cmd.cmd_id, seen->state, seen->progress_pct,
                            seen->value_pct, seen->err);
        return;
    }

    dedup_remember(cmd.cmd_id, now_sec);
    link_publish_ack(cmd.cmd_id, "ACK_RECEIVED");   /* фаза 1, до всякого руху */

    snprintf(job.cmd_id, sizeof job.cmd_id, "%s", cmd.cmd_id);
    job.target_pct = cmd.target_pct;
    if (!actuator_submit(&job)) {
        link_publish_status(cmd.cmd_id, "FAILED", 0, actuator_position(), ERR_BUSY);
        dedup_update(cmd.cmd_id, "FAILED", 0, actuator_position(), ERR_BUSY);
    }
}

/* --- Сценарій стенда ----------------------------------------------------- */

static void make_payload(char *buf, size_t cap, const char *cmd_id,
                         int target, uint32_t issued, uint32_t ttl)
{
    snprintf(buf, cap,
             "{\"cmd_id\":\"%s\",\"op\":\"set_valve_position\",\"target_pct\":%d,"
             "\"issued_at\":%u,\"ttl_sec\":%u}",
             cmd_id, target, (unsigned)issued, (unsigned)ttl);
}

int main(void)
{
    char buf[192];

    dedup_reset();
    actuator_init(g_now_ms);

    puts("== 1. Звичайна команда: відкрити засувку ==");
    make_payload(buf, sizeof buf, "6f21-open", 100, hal_epoch_sec(), 60u);
    handle_incoming_downlink(buf);
    run_for(1200u);

    puts("== 2. Сервер не дочекався квитанції і повторив пакет ==");
    handle_incoming_downlink(buf);
    run_for(4000u);

    puts("== 3. Наказ пролежав довше за TTL ==");
    make_payload(buf, sizeof buf, "6f21-stale", 0, hal_epoch_sec() - 300u, 5u);
    handle_incoming_downlink(buf);
    run_for(200u);

    puts("== 4. Вал заклинило: воркер сам закриває транзакцію ==");
    g_jammed = true;
    make_payload(buf, sizeof buf, "6f21-close", 0, hal_epoch_sec(), 60u);
    handle_incoming_downlink(buf);
    run_for(7000u);

    puts("== 5. Просідання живлення посеред маневру ==");
    g_jammed = false;
    make_payload(buf, sizeof buf, "6f21-half", 40, hal_epoch_sec(), 60u);
    handle_incoming_downlink(buf);
    run_for(600u);
    dedup_reset();                /* RAM після скидання чиста */
    actuator_init(g_now_ms);      /* RTC-пам'ять — ні: звітуємо про незавершений хід */
    run_for(200u);

    puts("== кінець ==");
    return 0;
}

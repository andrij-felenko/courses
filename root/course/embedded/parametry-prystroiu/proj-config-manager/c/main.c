/* main.c — прогін життєвих сценаріїв менеджера на моделі Flash. */
#include "cfg_manager.h"
#include "flash_sim.h"

#include <stdio.h>
#include <string.h>

/* Кладемо в сектор запис старої схеми — так виглядає Flash приладу,
   що тільки-но прийняв прошивку v2.0 по повітрю. */
static void seed_legacy_v1_record(uint8_t slot, uint32_t seq)
{
    cfg_payload_v1_t v1;
    memset(&v1, 0, sizeof v1);
    snprintf(v1.wifi_ssid, sizeof v1.wifi_ssid, "%s", "Field_AP_17");
    snprintf(v1.wifi_pass, sizeof v1.wifi_pass, "%s", "old-secret");
    v1.broker_ip[0] = 10;
    v1.broker_ip[1] = 0;
    v1.broker_ip[2] = 1;
    v1.broker_ip[3] = 5;
    v1.report_interval_s = 30;

    const cfg_header_t hdr = {
        .magic           = CFG_MAGIC,
        .schema_version  = CFG_SCHEMA_V1,
        .flags           = 0,
        .sequence_number = seq,
        .payload_len     = (uint16_t)sizeof v1,
        .reserved        = 0,
        .crc32           = cfg_crc32(&v1, sizeof v1),
    };

    flash_erase(slot);
    flash_program(slot, sizeof hdr, &v1, sizeof v1);
    flash_program(slot, 0, &hdr, sizeof hdr);
}

static void show(const char *tag)
{
    const cfg_payload_v2_t *c = cfg_live();
    printf("  %s: %s:%u tls=%u звіт=%u с таймаут=%u с (Slot %c, seq=%u)\n",
           tag, c->broker_host, c->broker_port, c->tls_enable,
           c->report_interval_s, c->conn_timeout_s,
           cfg_active_slot() ? 'B' : 'A', cfg_sequence());
}

int main(void)
{
    printf("== Холодний старт після конвеєра ==\n");
    flash_sim_wipe();
    if (cfg_manager_init() != CFG_OK) {
        return 1;
    }
    show("заводський профіль");

    printf("\n== Старт прошивки v2.0 поверх запису схеми v1 ==\n");
    flash_sim_wipe();
    seed_legacy_v1_record(0, 7);
    if (cfg_manager_init() != CFG_OK) {
        return 1;
    }
    show("після міграції");

    printf("\n-- Тест 1: суперечливі параметри --\n");
    cfg_payload_v2_t bad = *cfg_live();
    bad.report_interval_s = 60;
    bad.conn_timeout_s    = 10;
    printf("  результат: %s\n", cfg_strerror(cfg_start_trial(&bad)));

    printf("\n-- Тест 2: недосяжний брокер, випробування добігає таймауту --\n");
    cfg_payload_v2_t unreachable = *cfg_live();
    snprintf(unreachable.broker_host, CFG_HOST_LEN, "%s", "broken-server.invalid");
    unreachable.report_interval_s = 30;
    unreachable.conn_timeout_s    = 180;
    if (cfg_start_trial(&unreachable) == CFG_OK) {
        show("у випробуванні");
        for (uint32_t sec = 0; sec < CFG_TRIAL_TIMEOUT_S; ++sec) {
            cfg_timer_tick_1hz();   /* handshake так і не стався */
        }
        show("після відкату");
    }

    printf("\n-- Тест 3: валідний кандидат і підтверджений сеанс --\n");
    cfg_payload_v2_t good = *cfg_live();
    snprintf(good.broker_host, CFG_HOST_LEN, "%s", "prod-mqtt.example.net");
    good.broker_port = 8883;
    if (cfg_start_trial(&good) == CFG_OK) {
        printf("  TLS піднявся, брокер відповів PINGRESP — фіксуємо\n");
        printf("  фіксація: %s\n", cfg_strerror(cfg_confirm_commit()));
        show("активний профіль");
    }

    printf("\n== Перезавантаження з тим, що лежить у Flash ==\n");
    if (cfg_manager_init() != CFG_OK) {
        return 1;
    }
    show("після перезавантаження");
    return 0;
}

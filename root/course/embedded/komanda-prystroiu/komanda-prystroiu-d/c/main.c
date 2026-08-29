/* Демонстрація диспетчера команд на модельному часі.
 *
 * Кожен сценарій — це реальна мережева пастка зі статті: загублений квиток і
 * повтор, залп після сну, зрив на залізі, вичерпаний строк, повтор з ефіру,
 * зникнення живлення посеред руху. Сервер тут — це функції build()/deliver(),
 * прошивка — dispatcher_tick() у циклі.
 *
 * Збірка: cc -std=c11 -Wall -Wextra *.c -o cmddemo */

#include <limits.h>
#include <stdio.h>
#include <string.h>

#include "actuator.h"
#include "cmd_proto.h"
#include "dispatcher.h"
#include "journal.h"
#include "platform.h"

/* Готовий кадр на боці сервера. Повтор — це передавання ТИХ САМИХ байтів:
 * той самий токен, той самий seq, та сама контрольна сума. */
typedef struct {
    uint8_t buf[CMD_MAX_FRAME];
    size_t  len;
} frame_t;

static uint32_t g_seq = 0;

static frame_t build(uint8_t type, uint64_t token, uint32_t ttl_ms,
                     const uint8_t *payload, uint8_t plen) {
    cmd_frame_t f;
    memset(&f, 0, sizeof(f));
    f.type        = type;
    f.token       = token;
    f.seq         = ++g_seq;
    f.ttl_ms      = ttl_ms;
    f.payload_len = plen;
    if (plen > 0) memcpy(f.payload, payload, plen);

    frame_t out;
    out.len = wire_build_command(&f, out.buf, sizeof(out.buf));
    return out;
}

static void deliver(dispatcher_t *d, const frame_t *fr) {
    dispatcher_on_frame(d, fr->buf, fr->len);
}

/* Прокрутка головного циклу прошивки: тік кожні 50 мс модельного часу. */
static void run_ms(dispatcher_t *d, uint32_t ms) {
    for (uint32_t t = 0; t < ms; t += 50) {
        plat_advance_ms(50);
        dispatcher_tick(d);
    }
}

int main(void) {
    dispatcher_t disp;
    dispatcher_init(&disp);
    actuator_init();
    journal_commit();          /* чистий журнал: пристрій із заводу */

    uint8_t pl[CMD_MAX_PAYLOAD];

    /* ── 1. Штатне перемикання реле ─────────────────────────────────── */
    plat_banner("1. Абсолютна команда: SET_RELAY(0, ON)");
    pl[0] = 0; pl[1] = 1;
    frame_t relay_on = build(CMD_SET_RELAY, 0xA1A1A1A1u, 3000, pl, 2);
    deliver(&disp, &relay_on);
    run_ms(&disp, 100);

    /* ── 2. Битий кадр ──────────────────────────────────────────────── */
    plat_banner("2. Завада зіпсувала байт корисних даних");
    frame_t broken = relay_on;
    broken.buf[CMD_HDR_LEN] ^= 0x40u;      /* сервер такого не надсилав */
    deliver(&disp, &broken);

    /* ── 3. Втрачений квиток і повтор неідемпотентної дії ───────────── */
    plat_banner("3. Доза 20 мл: повтор під час роботи і повтор після завершення");
    wire_put_u16(pl, 20);
    frame_t dose = build(CMD_DISPENSE_ML, 0xB2B2B2B2u, 6000, pl, 2);
    deliver(&disp, &dose);
    run_ms(&disp, 500);
    printf("  (зворотний квиток загубився в ефірі — сервер шле той самий кадр)\n");
    deliver(&disp, &dose);                 /* насос уже працює */
    run_ms(&disp, 2000);
    printf("  (другий квиток теж загубився — сервер шле кадр утретє)\n");
    deliver(&disp, &dose);                 /* доза давно налита: віддаємо кеш */

    /* ── 4. Залп накопичених команд після глибокого сну ─────────────── */
    plat_banner("4. Пробудження: брокер вистрілює трьома командами поспіль");
    wire_put_i32(pl, 100);
    frame_t stale = build(CMD_GOTO_POS, 0xC001u, 0, pl, 4);      /* шлюз з'їв увесь TTL */
    wire_put_i32(pl, 400);
    frame_t middle = build(CMD_GOTO_POS, 0xC002u, 4000, pl, 4);
    wire_put_i32(pl, 250);
    frame_t fresh = build(CMD_GOTO_POS, 0xC003u, 4000, pl, 4);
    deliver(&disp, &stale);
    deliver(&disp, &middle);
    deliver(&disp, &fresh);
    run_ms(&disp, 1200);

    /* ── 5. Зрив на залізі посеред руху ─────────────────────────────── */
    plat_banner("5. Механічна перешкода: струмовий захист");
    actuator_set_stall_at(400);
    wire_put_i32(pl, 800);
    frame_t jam = build(CMD_GOTO_POS, 0xD00Du, 5000, pl, 4);
    deliver(&disp, &jam);
    run_ms(&disp, 1500);
    actuator_set_stall_at(INT32_MIN);

    /* ── 6. Строк вичерпано під час тривалої операції ────────────────── */
    plat_banner("6. Калібрування (1500 мс) із строком життя 600 мс");
    frame_t calib = build(CMD_CALIBRATE, 0xE1E1u, 600, NULL, 0);
    deliver(&disp, &calib);
    run_ms(&disp, 1000);

    /* ── 7. Повтор з ефіру після витіснення токена з кільця ──────────── */
    plat_banner("7. Кільце змилося: заповнюємо його поточним трафіком");
    for (int i = 0; i < 16; ++i) {
        frame_t noop = build(CMD_NOOP, 0xF0000000u + (uint32_t)i, 2000, NULL, 0);
        deliver(&disp, &noop);
        run_ms(&disp, 50);
    }
    printf("\n  (зловмисник випромінює записаний годину тому кадр SET_RELAY)\n");
    deliver(&disp, &relay_on);   /* токена в кільці вже немає — ловить лічильник seq */

    /* ── 8. Зникнення живлення посеред дозування ────────────────────── */
    plat_banner("8. Скидання живлення під час наливання");
    wire_put_u16(pl, 30);
    frame_t big_dose = build(CMD_DISPENSE_ML, 0xE7E7E7E7u, 8000, pl, 2);
    deliver(&disp, &big_dose);
    run_ms(&disp, 900);          /* насос у роботі */

    plat_power_cycle();
    dispatcher_init(&disp);      /* SRAM порожня: кільце й черга зникли */
    actuator_init();
    dispatcher_boot_recover(&disp);

    printf("\n  (сервер так і не дочекався другого квитка й повторює дозу)\n");
    deliver(&disp, &big_dose);   /* журнал урятував від другої дози */
    run_ms(&disp, 200);

    dispatcher_print_stats(&disp);
    return 0;
}

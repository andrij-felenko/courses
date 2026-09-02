/*
 * Накопичувальний котел 3 кВт: таблиця правил приїжджає з хаба кадром,
 * рушій крутиться в прошивці й тримає бак навіть тоді, коли каналу немає.
 */
#include <stdio.h>
#include <string.h>

#include "rule_engine.h"
#include "rule_frame.h"

/* карта регістрів установки */
#define R_TEMP   0x00u   /* температура теплоносія, Q16.16 °C */
#define R_FLOW   0x01u   /* протік, Q16.16 л/хв */
#define R_PRICE  0x02u   /* біржова ціна, Q16.16 $/кВт·год */
#define R_HEATER 0x10u   /* реле ТЕНа */
#define R_PUMP   0x11u   /* реле циркуляційного насоса */
#define R_TARGET 0x20u   /* уставка температури бака */
#define T_FLOW   (REG_TIMER_FIRST + 0u)

#define HUB_LEASE_MS   3000u
#define FLOW_GRACE_MS  5000u
#define TICK_MS        100u

static uint8_t build_rules(rule_descriptor_t *out) {
    uint8_t n = 0;

    /* 1. Останній рубіж: кипіння. Фіксується, поки людина не скине аварію. */
    out[n++] = (rule_descriptor_t){
        .rule_id = 1,
        .flags = RULE_FLAG_ENABLED | RULE_FLAG_SAFETY_CRITICAL | RULE_FLAG_LATCHING,
        .cond_op = OP_GREATER_THAN, .input_reg = R_TEMP, .threshold = Q16(85.0),
        .action_op = ACT_EMERGENCY_STOP, .output_target = R_HEATER, .action_param = 0 };

    /* 2. Протік упав — заводимо витримку 5 с; повернувся — знімаємо. */
    out[n++] = (rule_descriptor_t){
        .rule_id = 2,
        .flags = RULE_FLAG_ENABLED | RULE_FLAG_SAFETY_CRITICAL | RULE_FLAG_INVERT_ACTION,
        .cond_op = OP_LESS_THAN, .input_reg = R_FLOW, .threshold = Q16(2.0),
        .action_op = ACT_ARM_TIMER, .output_target = T_FLOW,
        .action_param = (int16_t)FLOW_GRACE_MS };

    /* 3. Витримка вичерпалась — аварійний стоп із фіксацією. */
    out[n++] = (rule_descriptor_t){
        .rule_id = 3,
        .flags = RULE_FLAG_ENABLED | RULE_FLAG_SAFETY_CRITICAL | RULE_FLAG_LATCHING,
        .cond_op = OP_TIMER_EXPIRED, .input_reg = T_FLOW, .threshold = (int32_t)FLOW_GRACE_MS,
        .action_op = ACT_EMERGENCY_STOP, .output_target = R_HEATER, .action_param = 0 };

    /* 4. Насос крутиться завжди, поки немає аварії. */
    out[n++] = (rule_descriptor_t){
        .rule_id = 4, .flags = RULE_FLAG_ENABLED,
        .cond_op = OP_ALWAYS, .input_reg = 0, .threshold = 0,
        .action_op = ACT_OUTPUT_SET, .output_target = R_PUMP, .action_param = 1 };

    /* 5. Оптимізація витрат: дешева електрика — гріємо, подорожчала — вимикаємо. */
    out[n++] = (rule_descriptor_t){
        .rule_id = 5, .flags = RULE_FLAG_ENABLED | RULE_FLAG_INVERT_ACTION,
        .cond_op = OP_LESS_THAN, .input_reg = R_PRICE, .threshold = Q16(0.05),
        .action_op = ACT_OUTPUT_SET, .output_target = R_HEATER, .action_param = 1 };

    /* 6. Перед самим порогом кипіння дистанційні уставки не приймаємо. */
    out[n++] = (rule_descriptor_t){
        .rule_id = 6, .flags = RULE_FLAG_ENABLED | RULE_FLAG_INVERT_ACTION,
        .cond_op = OP_GREATER_THAN, .input_reg = R_TEMP, .threshold = Q16(80.0),
        .action_op = ACT_INHIBIT_REMOTE, .output_target = R_TARGET, .action_param = 0 };

    /* 7. Зв'язку немає: ціна застаріла, гріти нічим не виправдано.
          Стоїть у таблиці після правила 5, тож слово за ним. */
    out[n++] = (rule_descriptor_t){
        .rule_id = 7, .flags = RULE_FLAG_ENABLED | RULE_FLAG_FALLBACK_ACTIVE,
        .cond_op = OP_ALWAYS, .input_reg = 0, .threshold = 0,
        .action_op = ACT_OUTPUT_SET, .output_target = R_HEATER, .action_param = 0 };

    return n;
}

static void hub_send(rule_engine_t *e, const rule_descriptor_t *table, uint8_t n,
                     bool corrupt, const char *what) {
    uint8_t frame[FRAME_MAX_SIZE];
    uint8_t reply[FRAME_REPLY_SIZE];
    size_t  reply_len = 0;

    size_t len = rule_frame_encode_table(table, n, frame, sizeof frame);
    if (len == 0) { printf("хаб: кадр не склався\n"); return; }
    if (corrupt) { frame[FRAME_HEADER_SIZE + 3] ^= 0x20u; }  /* один перевернутий біт */

    rule_error_t err = rule_frame_handle(e, frame, len, reply, sizeof reply, &reply_len);
    printf("  %-38s кадр %3u Б → %s(%u Б) %s\n", what, (unsigned)len,
           (err == ERR_NONE) ? "ACK" : "NACK", (unsigned)reply_len, rule_error_str(err));
}

/* Груба модель бака: 3 кВт у воду, тепловтрати, локальний перегрів без протоку. */
static void plant_step(rule_engine_t *e) {
    float temp = q16_to_float(rule_engine_read(e, R_TEMP));
    float flow = q16_to_float(rule_engine_read(e, R_FLOW));
    bool  heat = rule_engine_read(e, R_HEATER) != 0;

    if (heat) { temp += (flow >= 2.0f) ? 0.15f : 0.45f; }
    else      { temp -= 0.05f; }

    rule_engine_set_sensor(e, R_TEMP, Q16(temp));
}

static void report(const rule_engine_t *e, uint32_t t, const char *event) {
    static int32_t prev = -1;
    int32_t now = (rule_engine_read(e, R_HEATER) << 0)
                | (rule_engine_read(e, R_PUMP) << 1)
                | (rule_engine_read(e, REG_STATUS_WORD) << 2)
                | ((rule_engine_read(e, T_FLOW) != 0) ? (1 << 8) : 0);

    if (event == NULL && now == prev) { return; }
    prev = now;

    printf("%6.1f с | T=%5.1f°C  протік=%4.1f  ціна=%.3f | ТЕН=%d насос=%d "
           "витримка=%5d мс |%s%s%s %s\n",
           (double)t / 1000.0,
           (double)q16_to_float(rule_engine_read(e, R_TEMP)),
           (double)q16_to_float(rule_engine_read(e, R_FLOW)),
           (double)q16_to_float(rule_engine_read(e, R_PRICE)),
           (int)rule_engine_read(e, R_HEATER), (int)rule_engine_read(e, R_PUMP),
           (int)rule_engine_read(e, T_FLOW),
           e->fallback  ? " БЕЗ ЗВ'ЯЗКУ" : "",
           e->emergency ? " АВАРІЯ" : "",
           e->latched   ? " ФІКСАЦІЯ" : "",
           event ? event : "");
}

int main(void) {
    rule_engine_t engine;
    rule_engine_init(&engine, HUB_LEASE_MS, 0);
    rule_engine_set_sensor(&engine, R_TEMP,  Q16(40.0));
    rule_engine_set_sensor(&engine, R_FLOW,  Q16(6.0));
    rule_engine_set_sensor(&engine, R_PRICE, Q16(0.08));

    rule_descriptor_t table[MAX_RULES_COUNT];
    uint8_t n = build_rules(table);

    puts("=== завантаження таблиці правил ===");
    hub_send(&engine, table, n, false, "повна таблиця");
    hub_send(&engine, table, n, true,  "той самий кадр з побитим байтом");

    /* Хаб пробує лишити тільки «зручні» правила — захист має встояти. */
    rule_descriptor_t stripped[MAX_RULES_COUNT];
    uint8_t m = 0;
    for (uint8_t i = 0; i < n; ++i) {
        if ((table[i].flags & RULE_FLAG_SAFETY_CRITICAL) == 0) { stripped[m++] = table[i]; }
    }
    hub_send(&engine, stripped, m, false, "таблиця без правил безпеки");

    /* І спроба підсунути неіснуючий опкод. */
    rule_descriptor_t bogus[MAX_RULES_COUNT];
    memcpy(bogus, table, (size_t)n * sizeof table[0]);
    bogus[4].cond_op = 0x7F;
    hub_send(&engine, bogus, n, false, "правило з чужим кодом умови");

    printf("активних правил у прошивці: %u\n\n=== робота установки ===\n", engine.rule_count);

    for (uint32_t t = 0; t <= 34000u; t += TICK_MS) {
        const char *event = NULL;

        switch (t) {
            case 1000:
                rule_engine_set_sensor(&engine, R_PRICE, Q16(0.045));
                event = "<- ціна впала до 0.045 $/кВт·год";
                break;
            case 9000:
                event = "<- обрив магістрального каналу: хаб замовк";
                break;
            case 14000:
                event = "<- канал відновлено";
                break;
            case 16000:
                rule_engine_set_sensor(&engine, R_FLOW, Q16(0.3));
                event = "<- заклинило підшипник насоса";
                break;
            case 28000:
                rule_engine_reset_alarm(&engine);
                event = "<- оператор скидає аварію (протоку ще немає)";
                break;
            case 30000:
                rule_engine_set_sensor(&engine, R_FLOW, Q16(6.0));
                event = "<- насос замінено";
                break;
            case 31000:
                rule_engine_reset_alarm(&engine);
                event = "<- скидання аварії";
                break;
            default:
                break;
        }

        /* Серцебиття від хаба поновлює оренду керування щотакту. */
        if (t < 9000u || t >= 14000u) { rule_engine_hub_heartbeat(&engine, t); }

        rule_engine_tick(&engine, t);
        plant_step(&engine);
        report(&engine, t, event);
    }

    /* Хаб намагається підняти уставку, коли бак уже гарячий. */
    rule_error_t w = rule_engine_remote_write(&engine, R_TARGET, Q16(90.0));
    printf("\nдистанційна уставка 90 °C: %s\n", rule_error_str(w));
    return 0;
}

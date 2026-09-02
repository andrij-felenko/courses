/* Демонстрація кодека: збираємо кадр, розбираємо назад, а тоді женемо
   через парсер ті самі негативні вектори, що CI ганяє на Python.
   Ненульовий код повернення — сигнал для кроку конвеєра. */

#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "telemetry_protocol.h"

static int failures = 0;

static void dump(const char *label, const uint8_t *buf, size_t len)
{
    printf("%-18s", label);
    for (size_t i = 0; i < len; ++i) {
        printf(" %02X", buf[i]);
    }
    printf("   (%zu байт)\n", len);
}

static void expect(const char *what, proto_status_t got, proto_status_t want)
{
    int ok = (got == want);
    if (!ok) {
        ++failures;
    }
    printf("  %-34s -> %-24s %s\n", what, proto_status_str(got), ok ? "ok" : "ПРОВАЛ");
}

/* Кує кадр із довільним заголовком — саме такі приходять від чужої
   реалізації або з шумного каналу. Сума рахується по тому, що ФІЗИЧНО
   лежить у буфері, тож брехня в declared_len не маскується ще й битою
   сумою: кожен вектор перевіряє рівно одну ваду. */
static size_t forge(uint8_t *out, uint8_t version, uint8_t msg_id, uint8_t seq_id,
                    uint16_t declared_len, const uint8_t *payload, size_t payload_len)
{
    size_t total = PROTO_HEADER_LEN + payload_len + PROTO_FOOTER_LEN;
    assert(total <= PROTO_MAX_FRAME);

    out[0] = (uint8_t)PROTO_SOF;
    out[1] = version;
    out[2] = msg_id;
    out[3] = seq_id;
    out[4] = (uint8_t)(declared_len & 0xFFu);
    out[5] = (uint8_t)(declared_len >> 8);
    if (payload_len > 0) {
        memcpy(&out[PROTO_HEADER_LEN], payload, payload_len);
    }

    uint16_t crc = proto_crc16(&out[1], (size_t)(PROTO_HEADER_LEN - 1) + payload_len);
    out[total - 3] = (uint8_t)(crc & 0xFFu);
    out[total - 2] = (uint8_t)(crc >> 8);
    out[total - 1] = (uint8_t)PROTO_EOF;
    return total;
}

static void print_frame(const proto_frame_t *f)
{
    switch (f->msg_id) {
    case MSG_TELEMETRY_REPORT:
        printf("seq=0x%02X  T=%.2f C  p=%.1f hPa  U=%u mV  alert=%d  fault=%d\n",
               f->seq_id,
               (double)proto_temperature_c(&f->payload.telemetry),
               (double)proto_pressure_hpa(&f->payload.telemetry),
               f->payload.telemetry.voltage_mv,
               proto_alert_active(&f->payload.telemetry),
               proto_sensor_fault(&f->payload.telemetry));
        break;
    case MSG_CMD_SET_CONFIG:
        printf("seq=0x%02X  cmd_set_config: %u Гц, поріг %.2f C, прапорці 0x%02X\n",
               f->seq_id,
               f->payload.set_config.sample_rate_hz,
               (double)proto_alert_threshold_c(&f->payload.set_config),
               f->payload.set_config.flags_enable);
        break;
    case MSG_CMD_RESPONSE:
        printf("seq=0x%02X  cmd_response: на seq=0x%02X статус %s\n",
               f->seq_id,
               f->payload.ack.target_seq_id,
               proto_status_code_str(f->payload.ack.status));
        break;
    case MSG_CMD_PING:
        printf("seq=0x%02X  cmd_ping: навантаження немає\n", f->seq_id);
        break;
    }
}

/* Проганяє кадр туди-назад: зібрали, розібрали, надрукували. */
static void roundtrip(const proto_frame_t *tx)
{
    uint8_t wire[PROTO_MAX_FRAME];
    proto_frame_t rx;

    size_t n = proto_build_frame(tx, wire, sizeof wire);
    if (n == 0) {
        fprintf(stderr, "кадр msg_id=0x%02X не зібрався\n", (unsigned)tx->msg_id);
        ++failures;
        return;
    }
    proto_status_t st = proto_parse_frame(wire, n, &rx);
    if (st != STATUS_OK) {
        fprintf(stderr, "розбір власного кадру: %s\n", proto_status_str(st));
        ++failures;
        return;
    }
    print_frame(&rx);
}

int main(void)
{
    /* Класичний контрольний вектор CRC-16/CCITT-FALSE. */
    assert(proto_crc16((const uint8_t *)"123456789", 9) == 0x29B1);

    uint8_t frame[PROTO_MAX_FRAME];
    uint8_t bad[PROTO_MAX_FRAME];
    proto_frame_t rx;

    proto_frame_t tx = {
        .version = PROTO_VERSION,
        .msg_id = MSG_TELEMETRY_REPORT,
        .seq_id = 0x4A,
        .payload.telemetry = {
            .temp_raw = 2450,       /* 24.50 °C */
            .pressure_raw = 10132,  /* 1013.2 hPa */
            .voltage_mv = 3300,
            .flags = PROTO_FLAG_ALERT,
            .reserved = 0x00
        }
    };

    size_t n = proto_build_frame(&tx, frame, sizeof frame);
    if (n == 0) {
        fprintf(stderr, "еталонний кадр не зібрався\n");
        return 1;
    }
    dump("Golden frame:", frame, n);

    proto_status_t st = proto_parse_frame(frame, n, &rx);
    if (st != STATUS_OK) {
        fprintf(stderr, "розбір власного кадру: %s\n", proto_status_str(st));
        return 1;
    }
    print_frame(&rx);

    /* Тіло телеметрії, зібране руками: 8 байтів рівно за схемою. */
    static const uint8_t body[PROTO_LEN_TELEMETRY] = {
        0x92, 0x09,  /* temp_raw     = 2450  */
        0x94, 0x27,  /* pressure_raw = 10132 */
        0xE4, 0x0C,  /* voltage_mv   = 3300  */
        0x01, 0x00   /* flags, reserved      */
    };

    puts("\nНегативні вектори:");

    expect("буфер коротший за мінімум", proto_parse_frame(frame, 4, &rx), ERR_INVALID_LEN);
    expect("немає куди складати", proto_parse_frame(frame, n, NULL), ERR_BAD_ARG);

    memcpy(bad, frame, n);
    bad[0] = 0x00;
    expect("сміття замість SOF", proto_parse_frame(bad, n, &rx), ERR_INVALID_SOF);

    memcpy(bad, frame, n);
    bad[n - 1] = 0x00;
    expect("обірваний EOF", proto_parse_frame(bad, n, &rx), ERR_INVALID_EOF);

    memcpy(bad, frame, n);
    bad[PROTO_HEADER_LEN] ^= 0x01;  /* один перевернутий біт у навантаженні */
    expect("перевернутий біт у payload", proto_parse_frame(bad, n, &rx), ERR_INVALID_CRC);

    /* Заголовок обіцяє 8 байтів, у буфері їх 4: ловимо це ДО читання полів,
       інакше парсер зачитав би чотири байти чужої пам'яті. */
    size_t m = forge(bad, PROTO_VERSION, MSG_TELEMETRY_REPORT, 0x01, 8, body, 4);
    expect("payload_len понад буфер", proto_parse_frame(bad, m, &rx), ERR_INVALID_LEN);

    /* А тут довжина й буфер сходяться — не сходиться тип: telemetry це 8. */
    m = forge(bad, PROTO_VERSION, MSG_TELEMETRY_REPORT, 0x02, 5, body, 5);
    expect("довжина не для цього типу", proto_parse_frame(bad, m, &rx), ERR_INVALID_LEN);

    m = forge(bad, PROTO_VERSION, 0x7F, 0x03, 2, body, 2);
    expect("невідомий msg_id", proto_parse_frame(bad, m, &rx), ERR_UNKNOWN_MSG);

    m = forge(bad, 0x02, MSG_TELEMETRY_REPORT, 0x04, 8, body, sizeof body);
    expect("чужа мажорна версія", proto_parse_frame(bad, m, &rx), ERR_UNSUPPORTED_VERSION);

    /* Від'ємна температура: 0xFEC8 у доповняльному коді = -312 = -3.12 °C. */
    puts("");
    tx.seq_id = 0x4B;
    tx.payload.telemetry.temp_raw = -312;
    tx.payload.telemetry.flags = PROTO_FLAG_SENSOR_FAULT;
    n = proto_build_frame(&tx, frame, sizeof frame);
    assert(n > 0 && frame[PROTO_HEADER_LEN] == 0xC8 && frame[PROTO_HEADER_LEN + 1] == 0xFE);
    st = proto_parse_frame(frame, n, &rx);
    if (st != STATUS_OK || rx.payload.telemetry.temp_raw != -312) {
        fprintf(stderr, "знак не пережив дороту: %s\n", proto_status_str(st));
        return 1;
    }
    print_frame(&rx);

    /* Решта гілок switch-on — той самий кодек, інше навантаження. */
    proto_frame_t cfg = {
        .version = PROTO_VERSION,
        .msg_id = MSG_CMD_SET_CONFIG,
        .seq_id = 0x10,
        .payload.set_config = { .sample_rate_hz = 100,
                                .alert_threshold_raw = 8500,
                                .flags_enable = 0x03 }
    };
    roundtrip(&cfg);

    proto_frame_t ack = {
        .version = PROTO_VERSION,
        .msg_id = MSG_CMD_RESPONSE,
        .seq_id = 0x11,
        .payload.ack = { .target_seq_id = 0x10, .status = STATUS_CODE_OK }
    };
    roundtrip(&ack);

    /* Кадр ping без навантаження — теж повноцінний кадр із сумою. */
    proto_frame_t ping = { .version = PROTO_VERSION, .msg_id = MSG_CMD_PING, .seq_id = 0x12 };
    n = proto_build_frame(&ping, frame, sizeof frame);
    dump("ping frame:", frame, n);
    expect("порожнє навантаження ping", proto_parse_frame(frame, n, &rx), STATUS_OK);

    printf("\n%s\n", failures == 0 ? "усі вектори зійшлися" : "Є РОЗБІЖНОСТІ");
    return failures == 0 ? 0 : 1;
}

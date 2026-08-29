/*
 * Стенд приймача: збираємо кадри збоку відправника й пропускаємо їх через
 * secure_frame_parse(), перевіряючи, що конвеєр відповідає саме тим статусом,
 * якого чекає протокол.
 */
#include <stdio.h>
#include <string.h>

#include "hmac_sha256.h"
#include "secure_frame.h"

static int failures = 0;

static void check(const char *name, int ok, const char *detail)
{
    printf("%-46s %s  %s\n", name, ok ? "[ ok ]" : "[FAIL]", detail);
    if (!ok) {
        ++failures;
    }
}

/* ---- бік відправника: серіалізація кадру ------------------------------- */

static void wr_u16le(uint8_t *p, uint16_t v)
{
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
}

static void wr_u32le(uint8_t *p, uint32_t v)
{
    for (unsigned i = 0; i < 4U; ++i) {
        p[i] = (uint8_t)(v >> (8U * i));
    }
}

static void wr_u64le(uint8_t *p, uint64_t v)
{
    for (unsigned i = 0; i < 8U; ++i) {
        p[i] = (uint8_t)(v >> (8U * i));
    }
}

/* Повертає довжину зібраного кадру або 0, якщо буфер замалий. */
static size_t build_frame(uint8_t *buf, size_t cap,
                          uint8_t msg_type, uint64_t seq, uint32_t timestamp,
                          const uint8_t *payload, uint16_t payload_len,
                          const uint8_t *key, size_t key_len)
{
    size_t signed_len = (size_t)SECURE_HEADER_SIZE + payload_len;
    size_t total      = signed_len + SECURE_TAG_SIZE;
    if (total > cap) {
        return 0;
    }

    wr_u16le(buf + 0, SECURE_FRAME_MAGIC);
    buf[2] = msg_type;
    buf[3] = 0;                     /* reserved */
    wr_u64le(buf + 4, seq);
    wr_u32le(buf + 12, timestamp);
    wr_u16le(buf + 16, payload_len);
    memcpy(buf + SECURE_HEADER_SIZE, payload, payload_len);

    hmac_sha256(key, key_len, buf, signed_len, buf + signed_len);
    return total;
}

/* ---- самоперевірка криптографії --------------------------------------- */

static int digest_equals(const uint8_t *got, const char *hex)
{
    for (unsigned i = 0; i < SHA256_DIGEST_SIZE; ++i) {
        unsigned expected = 0;
        if (sscanf(hex + 2U * i, "%2x", &expected) != 1 || got[i] != (uint8_t)expected) {
            return 0;
        }
    }
    return 1;
}

/*
 * Без цієї перевірки решта стенда безглузда: конвеєр однаково "працював би"
 * і з підробленим хешем, який завжди повертає нулі. Вектори — з FIPS 180-4
 * (SHA-256 від "abc") і RFC 4231, тест 2 (HMAC з ключем "Jefe").
 */
static void crypto_self_test(void)
{
    uint8_t digest[SHA256_DIGEST_SIZE];

    sha256((const uint8_t *)"abc", 3, digest);
    check("SHA-256(\"abc\") = вектор FIPS 180-4",
          digest_equals(digest, "ba7816bf8f01cfea414140de5dae2223"
                                "b00361a396177a9cb410ff61f20015ad"),
          "");

    const char *key = "Jefe";
    const char *msg = "what do ya want for nothing?";
    hmac_sha256((const uint8_t *)key, strlen(key),
                (const uint8_t *)msg, strlen(msg), digest);
    check("HMAC-SHA256 = вектор RFC 4231 #2",
          digest_equals(digest, "5bdcc146bf60754e6a042426089575c7"
                                "5a003f089d2739839dec58b964ec3843"),
          "");
}

/* ---- стенд ------------------------------------------------------------- */

#define MSG_SET_SERVO_ANGLE 0x01

int main(void)
{
    static const uint8_t key[16] = {
        'm','c','u','_','s','e','c','r','e','t','_','k','e','y','_','1'
    };
    const uint8_t payload[2] = { 0x00, 0x5A };      /* кут 90 градусів */
    const uint32_t base_time = 1700000000U;

    crypto_self_test();

    SecureChannel ch;
    secure_channel_init(&ch, key, sizeof key, /* max_drift_s = */ 10U);

    uint8_t frame[64];
    SecureCommand cmd;
    SecureStatus st;
    char detail[96];

    /* 1. Легітимний кадр: вікно порожнє, лічильник 100. */
    size_t len = build_frame(frame, sizeof frame, MSG_SET_SERVO_ANGLE,
                             100, base_time, payload, sizeof payload,
                             key, sizeof key);
    memset(&cmd, 0, sizeof cmd);
    st = secure_frame_parse(&ch, frame, len, base_time + 5U, &cmd);
    snprintf(detail, sizeof detail, "статус %s, кут %u",
             secure_status_str(st), st == SECURE_OK ? cmd.payload[1] : 0U);
    check("1. Легітимний кадр (seq=100)",
          st == SECURE_OK && cmd.msg_type == MSG_SET_SERVO_ANGLE
              && cmd.payload_len == 2 && cmd.payload[1] == 0x5A,
          detail);

    /* 2. Атака повтору: той самий байт у байт кадр удруге. Тег правильний —
     *    відсікає саме вікно, а не криптографія. */
    st = secure_frame_parse(&ch, frame, len, base_time + 6U, &cmd);
    snprintf(detail, sizeof detail, "статус %s", secure_status_str(st));
    check("2. Повтор того самого кадру", st == SECURE_ERR_REPLAY_DETECTED, detail);

    /* 3. Підміна навантаження: кадр із новим лічильником 101, у якому
     *    зловмисник перевернув один біт кута. Тег більше не сходиться. */
    len = build_frame(frame, sizeof frame, MSG_SET_SERVO_ANGLE,
                      101, base_time, payload, sizeof payload,
                      key, sizeof key);
    frame[SECURE_HEADER_SIZE + 1] ^= 0x01U;         /* 90 градусів -> 91 */
    uint64_t max_before = ch.window.max_seq;
    st = secure_frame_parse(&ch, frame, len, base_time + 7U, &cmd);
    snprintf(detail, sizeof detail, "статус %s, max_seq %llu -> %llu",
             secure_status_str(st),
             (unsigned long long)max_before,
             (unsigned long long)ch.window.max_seq);
    /* Вікно не зсунулося: підроблений кадр не витратив лічильник 101. */
    check("3. Змінений біт у навантаженні",
          st == SECURE_ERR_AUTH_FAILED && ch.window.max_seq == max_before, detail);

    /* 4. Запізнілий кадр у межах вікна: радіо переставило пакети місцями. */
    len = build_frame(frame, sizeof frame, MSG_SET_SERVO_ANGLE,
                      95, base_time, payload, sizeof payload,
                      key, sizeof key);
    st = secure_frame_parse(&ch, frame, len, base_time + 8U, &cmd);
    snprintf(detail, sizeof detail, "статус %s (max_seq лишається %llu)",
             secure_status_str(st), (unsigned long long)ch.window.max_seq);
    check("4. Запізнілий кадр у вікні (seq=95)", st == SECURE_OK, detail);

    /* 5. Кадр із-за краю вікна: лічильник на 65 менший за максимум.
     *    Тег правильний, але пам'яті про нього вже немає — відкидаємо. */
    len = build_frame(frame, sizeof frame, MSG_SET_SERVO_ANGLE,
                      100 - 65, base_time, payload, sizeof payload,
                      key, sizeof key);
    st = secure_frame_parse(&ch, frame, len, base_time + 9U, &cmd);
    snprintf(detail, sizeof detail, "статус %s", secure_status_str(st));
    check("5. Застарілий кадр поза вікном (seq=35)",
          st == SECURE_ERR_REPLAY_DETECTED, detail);

    printf("\n%s\n", failures == 0 ? "усі перевірки пройдено"
                                   : "Є ПРОВАЛЕНІ ПЕРЕВІРКИ");
    return failures == 0 ? 0 : 1;
}

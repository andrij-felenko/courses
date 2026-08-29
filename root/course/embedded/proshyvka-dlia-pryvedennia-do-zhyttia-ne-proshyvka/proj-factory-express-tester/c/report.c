#include "report.h"

#include <string.h>

#include "hal.h"

#define REPORT_CAPACITY 1024u
/* Хвіст звіту («verdict», «total_us», дужки) мусить влізти завжди, тому
 * місце під нього тримаємо зарезервованим від самого початку: обрізаний
 * посередині JSON оператор не розбере взагалі. */
#define REPORT_TAIL_RESERVE 96u

static char   s_buf[REPORT_CAPACITY];
static size_t s_len;
static bool   s_truncated;
static bool   s_first;

static void put_raw(const char *text, size_t len)
{
    if (s_len + len > REPORT_CAPACITY - REPORT_TAIL_RESERVE) {
        s_truncated = true;
        return;
    }
    memcpy(&s_buf[s_len], text, len);
    s_len += len;
}

static void put(const char *text)
{
    put_raw(text, strlen(text));
}

/* Рядки в звіті — наші власні літерали, але екрануємо все одно:
 * одна лапка в описі помилки зламала б парсер на стороні стенда. */
static void put_escaped(const char *text)
{
    for (const char *p = text; *p != '\0'; p++) {
        char c = *p;
        if (c == '"' || c == '\\') {
            char pair[2] = {'\\', c};
            put_raw(pair, sizeof(pair));
        } else if (c >= 0x20) {
            put_raw(&c, 1);
        } else {
            put(" ");
        }
    }
}

static void put_int(int32_t value)
{
    char digits[12];
    size_t n = 0;
    uint32_t magnitude = value < 0 ? (uint32_t)(-(int64_t)value) : (uint32_t)value;

    if (value < 0) {
        put("-");
    }
    do {
        digits[n++] = (char)('0' + (magnitude % 10u));
        magnitude /= 10u;
    } while (magnitude != 0u);

    while (n > 0) {
        n--;
        put_raw(&digits[n], 1);
    }
}

static const char *code_name(fct_result_t code)
{
    switch (code) {
    case FCT_PASS:       return "PASS";
    case FCT_FAIL:       return "FAIL";
    case FCT_TIMEOUT:    return "TIMEOUT";
    case FCT_BUS_LOCKED: return "BUS_LOCKED";
    case FCT_INVALID_ID: return "INVALID_ID";
    case FCT_SKIPPED:    return "SKIPPED";
    default:             return "UNKNOWN";
    }
}

void report_begin(void)
{
    s_len = 0;
    s_truncated = false;
    s_first = true;
    put("{\"fct\":[");
}

void report_add(const char *name, const fct_verdict_t *v, uint32_t duration_us)
{
    if (!s_first) {
        put(",");
    }
    s_first = false;

    put("{\"test\":\"");
    put_escaped(name);
    put("\",\"status\":\"");
    put(code_name(v->code));
    put("\",\"us\":");
    put_int((int32_t)duration_us);

    if (v->detail != NULL) {
        put(",\"detail\":\"");
        put_escaped(v->detail);
        put("\"");
    }
    if (v->unit != NULL) {
        put(",\"value\":");
        put_int(v->value);
        put(",\"unit\":\"");
        put_escaped(v->unit);
        put("\"");
    }
    put("}");
}

/* Хвіст пишеться в зарезервоване місце, тому перевірку на переповнення
 * не робить: резерв від початку рахований під найдовший можливий хвіст. */
static void put_tail(const char *text)
{
    size_t len = strlen(text);
    if (len > REPORT_CAPACITY - s_len) {
        len = REPORT_CAPACITY - s_len;
    }
    memcpy(&s_buf[s_len], text, len);
    s_len += len;
}

static void put_tail_int(uint32_t value)
{
    char digits[12];
    size_t n = 0;
    uint32_t magnitude = value;

    do {
        digits[n++] = (char)('0' + (magnitude % 10u));
        magnitude /= 10u;
    } while (magnitude != 0u);

    while (n > 0 && s_len < REPORT_CAPACITY) {
        n--;
        s_buf[s_len++] = digits[n];
    }
}

void report_finish(bool overall_pass, uint32_t total_us)
{
    put_tail("],\"verdict\":\"");
    put_tail(overall_pass ? "PASS" : "FAIL");
    put_tail("\",\"total_us\":");
    put_tail_int(total_us);
    if (s_truncated) {
        put_tail(",\"truncated\":true");
    }
    put_tail("}\r\n");

    hal_uart_write(s_buf, s_len);
}

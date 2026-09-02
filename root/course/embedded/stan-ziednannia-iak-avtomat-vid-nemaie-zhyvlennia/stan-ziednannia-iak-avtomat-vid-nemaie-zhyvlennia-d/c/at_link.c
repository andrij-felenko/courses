#include "at_link.h"

#include "modem_hal.h"

#include <string.h>

#define RX_RING_SZ    512u
#define RX_RING_MASK  (RX_RING_SZ - 1u)
#define RX_HIGH_WATER ((RX_RING_SZ * 4u) / 5u) /* 80 % — знімаємо RTS */
#define RX_LOW_WATER  (RX_RING_SZ / 2u)
#define LINE_MAX      192u
#define DATA_MAX      512u

static volatile uint8_t  s_ring[RX_RING_SZ];
static volatile uint16_t s_head;
static volatile uint16_t s_tail;
static volatile uint32_t s_overflows;
static volatile bool     s_rts_ready;

static char    s_line[LINE_MAX];
static size_t  s_line_len;
static uint8_t s_data[DATA_MAX];
static size_t  s_data_len;
static size_t  s_data_want; /* скільки байтів тіла +IPD ще чекаємо */

static uint16_t ring_fill(void)
{
    return (uint16_t)((s_head - s_tail) & RX_RING_MASK);
}

void at_link_init(void)
{
    s_head = 0;
    s_tail = 0;
    s_overflows = 0;
    s_line_len = 0;
    s_data_len = 0;
    s_data_want = 0;
    s_rts_ready = true;
    hal_uart_rts_set(true);
}

void at_link_rx_isr(uint8_t byte)
{
    uint16_t next = (uint16_t)((s_head + 1u) & RX_RING_MASK);
    if (next == s_tail) {
        /* Черга повна: втрачаємо ОДИН байт, а не всю чергу. Лічильник
           їде в телеметрію — переповнення означає надто рідкий tick. */
        s_overflows++;
        return;
    }
    s_ring[s_head] = byte;
    s_head = next;

    if (s_rts_ready && ring_fill() >= RX_HIGH_WATER) {
        s_rts_ready = false;
        hal_uart_rts_set(false); /* просимо модем зупинити потік */
    }
}

static bool ring_pop(uint8_t *out)
{
    if (s_head == s_tail) {
        return false;
    }
    *out = s_ring[s_tail];
    s_tail = (uint16_t)((s_tail + 1u) & RX_RING_MASK);

    if (!s_rts_ready && ring_fill() <= RX_LOW_WATER) {
        s_rts_ready = true;
        hal_uart_rts_set(true);
    }
    return true;
}

static bool starts_with(const char *s, const char *prefix)
{
    return strncmp(s, prefix, strlen(prefix)) == 0;
}

/* Читає наступне ціле, пропускаючи роздільники (':', ',', пробіли, літери). */
static bool next_int(const char *s, size_t *pos, int32_t *out)
{
    size_t i = *pos;
    while (s[i] != '\0' && (s[i] < '0' || s[i] > '9') && s[i] != '-') {
        i++;
    }
    if (s[i] == '\0') {
        *pos = i;
        return false;
    }
    bool neg = false;
    if (s[i] == '-') {
        neg = true;
        i++;
    }
    if (s[i] < '0' || s[i] > '9') {
        *pos = i;
        return false;
    }
    int32_t v = 0;
    while (s[i] >= '0' && s[i] <= '9') {
        v = v * 10 + (s[i] - '0');
        i++;
    }
    *pos = i;
    *out = neg ? -v : v;
    return true;
}

static void classify(const char *line, at_msg_t *out)
{
    out->value = 0;
    out->data = NULL;
    out->len = 0;

    if (strcmp(line, "OK") == 0) {
        out->kind = AT_MSG_OK;
        return;
    }
    if (strcmp(line, "ERROR") == 0) {
        out->kind = AT_MSG_ERROR;
        return;
    }
    if (starts_with(line, "+CME ERROR:") || starts_with(line, "+CMS ERROR:")) {
        size_t p = 11;
        int32_t code = 0;
        out->kind = AT_MSG_CME_ERROR;
        /* AT+CMEE=2 дає текст замість числа — тоді код невідомий (-1). */
        out->value = next_int(line, &p, &code) ? code : -1;
        return;
    }
    if (starts_with(line, "+CPIN:")) {
        out->kind = AT_MSG_CPIN;
        if (strstr(line, "READY") != NULL) {
            out->value = CPIN_READY;
        } else if (strstr(line, "SIM PIN") != NULL || strstr(line, "SIM PUK") != NULL) {
            out->value = CPIN_NEED_PIN;
        } else {
            out->value = CPIN_ABSENT; /* NOT INSERTED, SIM FAILURE */
        }
        return;
    }
    if (starts_with(line, "+CREG:") || starts_with(line, "+CEREG:")) {
        /* URC має один аргумент, відповідь на "?" — два: <n>,<stat>. */
        size_t p = 0;
        int32_t first = 0;
        int32_t second = 0;
        out->kind = AT_MSG_CREG;
        (void)next_int(line, &p, &first);
        out->value = next_int(line, &p, &second) ? second : first;
        return;
    }
    if (starts_with(line, "+CSQ:")) {
        size_t p = 0;
        int32_t idx = 0;
        out->kind = AT_MSG_CSQ;
        out->value = (next_int(line, &p, &idx) && idx <= 31) ? (-113 + 2 * idx) : RSSI_UNKNOWN;
        return;
    }
    if (starts_with(line, "+CGPADDR:")) {
        /* Контекст IPv4: адреса без крапок або 0.0.0.0 — це ще не адреса. */
        bool valid = (strchr(line, '.') != NULL) && (strstr(line, "0.0.0.0") == NULL);
        out->kind = valid ? AT_MSG_IP_READY : AT_MSG_UNKNOWN;
        return;
    }
    if (strcmp(line, "CONNECT OK") == 0 || starts_with(line, "+CIPOPEN: 0,0")) {
        out->kind = AT_MSG_CONNECT_OK;
        return;
    }
    if (strcmp(line, "SEND OK") == 0) {
        out->kind = AT_MSG_SEND_OK;
        return;
    }
    if (strstr(line, "CLOSED") != NULL) {
        out->kind = AT_MSG_CLOSED;
        return;
    }
    if (strstr(line, "DEACT") != NULL) { /* +CGEV: ME DEACT, PDP DEACT */
        out->kind = AT_MSG_PDP_DEACT;
        return;
    }
    if (strcmp(line, "RDY") == 0 || strcmp(line, "+CFUN: 1") == 0 ||
        starts_with(line, "*ATREADY")) {
        out->kind = AT_MSG_BOOT;
        return;
    }
    out->kind = AT_MSG_UNKNOWN; /* луна команди до ATE0, банери оператора */
}

bool at_link_poll(at_msg_t *out)
{
    uint8_t b;

    while (ring_pop(&b)) {
        if (s_data_want > 0) { /* тіло пакета з сокета */
            if (s_data_len < DATA_MAX) {
                s_data[s_data_len++] = b;
            }
            if (--s_data_want == 0) {
                out->kind = AT_MSG_DATA;
                out->value = 0;
                out->data = s_data;
                out->len = s_data_len;
                s_data_len = 0;
                return true;
            }
            continue;
        }

        if (b == '>' && s_line_len == 0) { /* запрошення AT+CIPSEND */
            out->kind = AT_MSG_PROMPT;
            out->value = 0;
            out->data = NULL;
            out->len = 0;
            return true;
        }
        if (b == '\r') {
            continue;
        }
        if (b == '\n') {
            if (s_line_len == 0) {
                continue; /* порожній рядок-роздільник */
            }
            s_line[s_line_len] = '\0';
            s_line_len = 0;
            classify(s_line, out);
            if (out->kind != AT_MSG_UNKNOWN) {
                return true;
            }
            continue;
        }
        /* Заголовок "+IPD,<len>:" закінчується двокрапкою, а не CRLF. */
        if (b == ':' && s_line_len >= 5 && memcmp(s_line, "+IPD,", 5) == 0) {
            size_t p = 5;
            int32_t n = 0;
            s_line[s_line_len] = '\0';
            s_line_len = 0;
            if (next_int(s_line, &p, &n) && n > 0) {
                s_data_want = (size_t)n; /* хвіст понад DATA_MAX буде відкинуто */
                s_data_len = 0;
            }
            continue;
        }
        if (s_line_len + 1u < LINE_MAX) {
            s_line[s_line_len++] = (char)b;
        } else {
            s_line_len = 0; /* рядок довший за буфер — викидаємо цілком */
        }
    }
    return false;
}

void at_link_send_line(const char *cmd)
{
    hal_uart_write((const uint8_t *)cmd, strlen(cmd));
    hal_uart_write((const uint8_t *)"\r\n", 2u);
}

void at_link_send_raw(const uint8_t *data, size_t len)
{
    hal_uart_write(data, len);
}

uint32_t at_link_overflows(void)
{
    return s_overflows;
}

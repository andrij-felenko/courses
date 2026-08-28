#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define AT_RX_RING_SIZE    1024
#define AT_LINE_BUF_SIZE   256
#define AT_MAX_URC_HANDLERS 16

/* Коди результату виконання транзакції */
typedef enum {
    AT_RESP_OK = 0,
    AT_RESP_ERROR,
    AT_RESP_TIMEOUT,
    AT_RESP_BUSY
} at_response_code_t;

/* Прототип функції зворотного виклику для URC */
typedef void (*at_urc_callback_t)(const char *urc_line, void *user_ctx);

/* Елемент таблиці реєстрації URC */
typedef struct {
    const char *prefix;
    at_urc_callback_t callback;
    void *user_ctx;
} at_urc_entry_t;

/* Стан кільцевого буфера UART */
typedef struct {
    uint8_t buffer[AT_RX_RING_SIZE];
    volatile size_t head;
    volatile size_t tail;
} at_ring_buf_t;

/* Стан поточної синхронної транзакції */
typedef struct {
    bool is_active;
    char *out_response_buf;
    size_t out_buf_max_len;
    uint32_t timeout_ms;
    uint32_t start_time_ms;
    at_response_code_t result;
    bool is_completed;
} at_transaction_t;

/* Головна структура драйвера модема */
typedef struct {
    at_ring_buf_t ring_rx;
    char line_accumulator[AT_LINE_BUF_SIZE];
    size_t line_len;
    
    at_urc_entry_t urc_table[AT_MAX_URC_HANDLERS];
    size_t urc_count;
    
    at_transaction_t current_cmd;
    bool prompt_detected;
    
    /* Апаратні абстракції платформи */
    void (*uart_write)(const uint8_t *data, size_t len);
    uint32_t (*get_tick_ms)(void);
} at_driver_t;

/* ── Ініціалізація та реєстрація URC ─────────────────────────────────────── */

void at_driver_init(at_driver_t *drv,
                    void (*uart_write_fn)(const uint8_t *, size_t),
                    uint32_t (*get_tick_fn)(void)) {
    memset(drv, 0, sizeof(at_driver_t));
    drv->uart_write = uart_write_fn;
    drv->get_tick_ms = get_tick_fn;
}

bool at_register_urc(at_driver_t *drv, const char *prefix, at_urc_callback_t cb, void *ctx) {
    if (drv->urc_count >= AT_MAX_URC_HANDLERS || !prefix || !cb) {
        return false;
    }
    drv->urc_table[drv->urc_count].prefix = prefix;
    drv->urc_table[drv->urc_count].callback = cb;
    drv->urc_table[drv->urc_count].user_ctx = ctx;
    drv->urc_count++;
    return true;
}

/* ── Обробка переривання UART RX (запис у кільцевий буфер) ───────────────── */

void at_driver_feed_rx_isr(at_driver_t *drv, uint8_t byte) {
    size_t next_head = (drv->ring_rx.head + 1) % AT_RX_RING_SIZE;
    if (next_head != drv->ring_rx.tail) {
        drv->ring_rx.buffer[drv->ring_rx.head] = byte;
        drv->ring_rx.head = next_head;
    }
    /* Переповнення буфера: байт відкидається для запобігання пошкодженню пам'яті */
}

/* ── Внутрішній диспетчер завершеного рядка ────────────────────────────────── */

static void at_dispatch_line(at_driver_t *drv, const char *line) {
    /* 1. Перевірка на збіг з зареєстрованими URC */
    for (size_t i = 0; i < drv->urc_count; i++) {
        size_t prefix_len = strlen(drv->urc_table[i].prefix);
        if (strncmp(line, drv->urc_table[i].prefix, prefix_len) == 0) {
            drv->urc_table[i].callback(line, drv->urc_table[i].user_ctx);
            return; /* URC оброблено, це не відповідь на поточну команду */
        }
    }

    /* 2. Перевірка на відповідність активній транзакції */
    if (!drv->current_cmd.is_active) {
        return; /* Неочікуваний рядок поза контекстом транзакції */
    }

    /* 3. Перевірка фінальних кодів успіху / помилки */
    if (strcmp(line, "OK") == 0 || strncmp(line, "CONNECT", 7) == 0) {
        drv->current_cmd.result = AT_RESP_OK;
        drv->current_cmd.is_completed = true;
        drv->current_cmd.is_active = false;
        return;
    }

    if (strcmp(line, "ERROR") == 0 ||
        strncmp(line, "+CME ERROR:", 11) == 0 ||
        strncmp(line, "+CMS ERROR:", 11) == 0 ||
        strcmp(line, "NO CARRIER") == 0 ||
        strcmp(line, "BUSY") == 0) {
        drv->current_cmd.result = AT_RESP_ERROR;
        drv->current_cmd.is_completed = true;
        drv->current_cmd.is_active = false;
        return;
    }

    /* 4. Проміжний рядок даних (копіюємо у буфер результату) */
    if (drv->current_cmd.out_response_buf && drv->current_cmd.out_buf_max_len > 0) {
        size_t cur_len = strlen(drv->current_cmd.out_response_buf);
        size_t line_len = strlen(line);
        if (cur_len + line_len + 2 < drv->current_cmd.out_buf_max_len) {
            if (cur_len > 0) {
                strcat(drv->current_cmd.out_response_buf, "\n");
            }
            strcat(drv->current_cmd.out_response_buf, line);
        }
    }
}

/* ── Фоновий кінцевий автомат парсера ─────────────────────────────────────── */

void at_driver_process(at_driver_t *drv) {
    /* Обробка тайм-ауту поточної транзакції */
    if (drv->current_cmd.is_active) {
        uint32_t now = drv->get_tick_ms();
        if (now - drv->current_cmd.start_time_ms >= drv->current_cmd.timeout_ms) {
            drv->current_cmd.result = AT_RESP_TIMEOUT;
            drv->current_cmd.is_completed = true;
            drv->current_cmd.is_active = false;
        }
    }

    /* Вичитування та нарізка байтів із кільцевого буфера */
    while (drv->ring_rx.head != drv->ring_rx.tail) {
        uint8_t ch = drv->ring_rx.buffer[drv->ring_rx.tail];
        drv->ring_rx.tail = (drv->ring_rx.tail + 1) % AT_RX_RING_SIZE;

        /* Спеціальний випадок: детекція промпту введення даних '> ' */
        if (ch == ' ' && drv->line_len == 1 && drv->line_accumulator[0] == '>') {
            drv->prompt_detected = true;
            drv->line_len = 0;
            continue;
        }

        if (ch == '\r' || ch == '\n') {
            if (drv->line_len > 0) {
                drv->line_accumulator[drv->line_len] = '\0';
                at_dispatch_line(drv, drv->line_accumulator);
                drv->line_len = 0;
            }
        } else {
            if (drv->line_len < AT_LINE_BUF_SIZE - 1) {
                drv->line_accumulator[drv->line_len++] = (char)ch;
            } else {
                /* Захист від переповнення рядка: скидання накопичувача */
                drv->line_len = 0;
            }
        }
    }
}

/* ── Відправка синхронної команди з очікуванням відповіді ─────────────────── */

at_response_code_t at_send_command_sync(at_driver_t *drv,
                                       const char *cmd,
                                       char *resp_buf,
                                       size_t resp_buf_size,
                                       uint32_t timeout_ms) {
    if (drv->current_cmd.is_active) {
        return AT_RESP_BUSY;
    }

    if (resp_buf && resp_buf_size > 0) {
        resp_buf[0] = '\0';
    }

    drv->current_cmd.out_response_buf = resp_buf;
    drv->current_cmd.out_buf_max_len = resp_buf_size;
    drv->current_cmd.timeout_ms = timeout_ms;
    drv->current_cmd.start_time_ms = drv->get_tick_ms();
    drv->current_cmd.result = AT_RESP_TIMEOUT;
    drv->current_cmd.is_completed = false;
    drv->current_cmd.is_active = true;

    /* Передача рядка команди у фізичний UART */
    drv->uart_write((const uint8_t *)cmd, strlen(cmd));
    drv->uart_write((const uint8_t *)"\r\n", 2);

    /* Неблокуючий цикл очікування виконання FSM */
    while (!drv->current_cmd.is_completed) {
        at_driver_process(drv);
    }

    return drv->current_cmd.result;
}

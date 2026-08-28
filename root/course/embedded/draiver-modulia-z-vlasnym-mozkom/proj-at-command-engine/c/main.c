#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define AT_RX_BUFFER_SIZE       512U
#define AT_MAX_LINE_SIZE        128U
#define AT_QUEUE_CAPACITY       8U
#define AT_MAX_URC_HANDLERS     8U

/* Типи результатів виконання AT-команд */
typedef enum {
    AT_STATUS_OK = 0,
    AT_STATUS_ERROR,
    AT_STATUS_TIMEOUT,
    AT_STATUS_ABORTED
} at_status_t;

/* Функція зворотного виклику для URC */
typedef void (*at_urc_cb_t)(const char *urc_line);

/* Функція зворотного виклику завершення команди */
typedef void (*at_cmd_complete_cb_t)(at_status_t status, const char *resp_data, void *ctx);

/* Елемент черги команд */
typedef struct {
    char                 cmd_text[AT_MAX_LINE_SIZE];
    char                 expect_prefix[32];
    uint32_t             timeout_ms;
    uint8_t              max_retries;
    uint8_t              current_retry;
    at_cmd_complete_cb_t callback;
    void                *ctx;
} at_cmd_item_t;

/* Запис у таблиці URC-обробників */
typedef struct {
    char          prefix[24];
    at_urc_cb_t   handler;
} at_urc_entry_t;

/* Стани автомата рушія */
typedef enum {
    AT_STATE_IDLE = 0,
    AT_STATE_SEND,
    AT_STATE_WAIT_RESPONSE,
    AT_STATE_RETRY_DELAY
} at_engine_state_t;

/* Головний контекст AT-рушія */
typedef struct {
    /* Кільцевий буфер прийому */
    uint8_t             rx_buf[AT_RX_BUFFER_SIZE];
    uint16_t            rx_tail;
    
    /* Черга команд (FIFO) */
    at_cmd_item_t       queue[AT_QUEUE_CAPACITY];
    uint8_t             q_head;
    uint8_t             q_tail;
    uint8_t             q_count;
    
    /* Таблиця URC */
    at_urc_entry_t      urc_table[AT_MAX_URC_HANDLERS];
    uint8_t             urc_count;
    
    /* Стан автомата та таймінги */
    at_engine_state_t   state;
    at_cmd_item_t       current_cmd;
    uint32_t            timer_start_ms;
    char                last_data_line[AT_MAX_LINE_SIZE];
    
    /* Апаратна функція передачі UART */
    void (*uart_tx_fn)(const uint8_t *data, size_t len);
    uint32_t (*get_tick_ms_fn)(void);
} at_engine_t;

/* Ініціалізація рушія */
void at_engine_init(at_engine_t *eng, 
                    void (*tx_fn)(const uint8_t *, size_t),
                    uint32_t (*tick_fn)(void)) {
    memset(eng, 0, sizeof(at_engine_t));
    eng->uart_tx_fn = tx_fn;
    eng->get_tick_ms_fn = tick_fn;
    eng->state = AT_STATE_IDLE;
}

/* Реєстрація URC-обробника */
bool at_engine_register_urc(at_engine_t *eng, const char *prefix, at_urc_cb_t handler) {
    if (eng->urc_count >= AT_MAX_URC_HANDLERS) {
        return false;
    }
    strncpy(eng->urc_table[eng->urc_count].prefix, prefix, sizeof(eng->urc_table[0].prefix) - 1);
    eng->urc_table[eng->urc_count].prefix[sizeof(eng->urc_table[0].prefix) - 1] = '\0';
    eng->urc_table[eng->urc_count].handler = handler;
    eng->urc_count++;
    return true;
}

/* Додавання команди в чергу */
bool at_engine_send_cmd(at_engine_t *eng, const char *cmd, const char *expect_prefix,
                        uint32_t timeout_ms, uint8_t retries, 
                        at_cmd_complete_cb_t cb, void *ctx) {
    if (eng->q_count >= AT_QUEUE_CAPACITY) {
        return false; /* Черга переповнена */
    }
    at_cmd_item_t *item = &eng->queue[eng->q_head];
    strncpy(item->cmd_text, cmd, sizeof(item->cmd_text) - 1);
    item->cmd_text[sizeof(item->cmd_text) - 1] = '\0';
    
    if (expect_prefix) {
        strncpy(item->expect_prefix, expect_prefix, sizeof(item->expect_prefix) - 1);
        item->expect_prefix[sizeof(item->expect_prefix) - 1] = '\0';
    } else {
        item->expect_prefix[0] = '\0';
    }
    
    item->timeout_ms = timeout_ms;
    item->max_retries = retries;
    item->current_retry = 0;
    item->callback = cb;
    item->ctx = ctx;
    
    eng->q_head = (uint8_t)((eng->q_head + 1U) % AT_QUEUE_CAPACITY);
    eng->q_count++;
    return true;
}

/* Виділення рядка з кільцевого буфера */
static bool at_extract_line(at_engine_t *eng, uint16_t dma_cndtr, char *out_line, size_t max_len) {
    uint16_t head = (uint16_t)(AT_RX_BUFFER_SIZE - dma_cndtr);
    uint16_t tail = eng->rx_tail;
    
    if (head == tail) return false;
    
    uint16_t scan = tail;
    bool found = false;
    while (scan != head) {
        if (eng->rx_buf[scan] == '\n') {
            found = true;
            break;
        }
        scan = (uint16_t)((scan + 1U) % AT_RX_BUFFER_SIZE);
    }
    
    if (!found) return false;
    
    size_t idx = 0;
    while (eng->rx_tail != scan) {
        uint8_t b = eng->rx_buf[eng->rx_tail];
        if (b != '\r' && b != '\n' && idx < max_len - 1U) {
            out_line[idx++] = (char)b;
        }
        eng->rx_tail = (uint16_t)((eng->rx_tail + 1U) % AT_RX_BUFFER_SIZE);
    }
    eng->rx_tail = (uint16_t)((eng->rx_tail + 1U) % AT_RX_BUFFER_SIZE); /* Пропуск '\n' */
    out_line[idx] = '\0';
    return (idx > 0);
}

/* Головний неблокуючий крок диспетчера AT-рушія */
void at_engine_poll(at_engine_t *eng, uint16_t dma_cndtr) {
    char line_buf[AT_MAX_LINE_SIZE];
    uint32_t now = eng->get_tick_ms_fn();

    /* 1. Потокова вичитка всіх доступних рядків та сепарація URC */
    while (at_extract_line(eng, dma_cndtr, line_buf, sizeof(line_buf))) {
        bool is_urc = false;
        for (uint8_t i = 0; i < eng->urc_count; ++i) {
            if (strncmp(line_buf, eng->urc_table[i].prefix, strlen(eng->urc_table[i].prefix)) == 0) {
                if (eng->urc_table[i].handler) {
                    eng->urc_table[i].handler(line_buf);
                }
                is_urc = true;
                break;
            }
        }
        
        if (is_urc) {
            continue; /* Рядок був URC, переходимо до наступного */
        }

        /* Обробка рядка в контексті активної команди */
        if (eng->state == AT_STATE_WAIT_RESPONSE) {
            if (eng->current_cmd.expect_prefix[0] != '\0' &&
                strncmp(line_buf, eng->current_cmd.expect_prefix, strlen(eng->current_cmd.expect_prefix)) == 0) {
                strncpy(eng->last_data_line, line_buf, sizeof(eng->last_data_line) - 1);
                eng->last_data_line[sizeof(eng->last_data_line) - 1] = '\0';
            } else if (strcmp(line_buf, "OK") == 0) {
                if (eng->current_cmd.callback) {
                    eng->current_cmd.callback(AT_STATUS_OK, eng->last_data_line, eng->current_cmd.ctx);
                }
                eng->state = AT_STATE_IDLE;
            } else if (strcmp(line_buf, "ERROR") == 0 || strstr(line_buf, "+CME ERROR:") != NULL) {
                if (eng->current_cmd.current_retry < eng->current_cmd.max_retries) {
                    eng->current_cmd.current_retry++;
                    eng->timer_start_ms = now;
                    eng->state = AT_STATE_RETRY_DELAY;
                } else {
                    if (eng->current_cmd.callback) {
                        eng->current_cmd.callback(AT_STATUS_ERROR, line_buf, eng->current_cmd.ctx);
                    }
                    eng->state = AT_STATE_IDLE;
                }
            }
        }
    }

    /* 2. Скінченний автомат керування чергою */
    switch (eng->state) {
        case AT_STATE_IDLE:
            if (eng->q_count > 0) {
                /* Вибірка наступної команди з черги */
                eng->current_cmd = eng->queue[eng->q_tail];
                eng->q_tail = (uint8_t)((eng->q_tail + 1U) % AT_QUEUE_CAPACITY);
                eng->q_count--;
                eng->last_data_line[0] = '\0';
                eng->state = AT_STATE_SEND;
            }
            break;

        case AT_STATE_SEND:
            eng->uart_tx_fn((const uint8_t *)eng->current_cmd.cmd_text, strlen(eng->current_cmd.cmd_text));
            eng->timer_start_ms = now;
            eng->state = AT_STATE_WAIT_RESPONSE;
            break;

        case AT_STATE_WAIT_RESPONSE:
            if ((uint32_t)(now - eng->timer_start_ms) >= eng->current_cmd.timeout_ms) {
                if (eng->current_cmd.current_retry < eng->current_cmd.max_retries) {
                    eng->current_cmd.current_retry++;
                    eng->timer_start_ms = now;
                    eng->state = AT_STATE_RETRY_DELAY;
                } else {
                    if (eng->current_cmd.callback) {
                        eng->current_cmd.callback(AT_STATUS_TIMEOUT, NULL, eng->current_cmd.ctx);
                    }
                    eng->state = AT_STATE_IDLE;
                }
            }
            break;

        case AT_STATE_RETRY_DELAY:
            /* Неблокуюча витримка 100 мс перед повторним надсиланням команди */
            if ((uint32_t)(now - eng->timer_start_ms) >= 100U) {
                eng->state = AT_STATE_SEND;
            }
            break;
    }
}

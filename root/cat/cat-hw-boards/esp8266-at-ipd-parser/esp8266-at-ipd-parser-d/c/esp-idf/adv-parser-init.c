#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

typedef enum {
    ADV_STATE_IDLE,
    ADV_STATE_PREFIX,
    ADV_STATE_LINK_ID,
    ADV_STATE_LEN,
    ADV_STATE_SKIP_INFO,
    ADV_STATE_PAYLOAD
} adv_fsm_state_t;

typedef struct {
    adv_fsm_state_t state;
    uint8_t prefix_idx;
    uint8_t link_id;
    uint16_t len;
    uint16_t read_bytes;
    bool is_multilink;
    bool cipdinfo_enabled;
    uint8_t comma_count;
    uint8_t payload[2048];
} adv_ipd_parser_t;

void adv_parser_init(adv_ipd_parser_t *p, bool multilink, bool cipdinfo) {
    p->state = ADV_STATE_IDLE;
    p->prefix_idx = 0;
    p->link_id = 0;
    p->len = 0;
    p->read_bytes = 0;
    p->is_multilink = multilink;
    p->cipdinfo_enabled = cipdinfo;
    p->comma_count = 0;
}

void adv_parser_feed(adv_ipd_parser_t *p, uint8_t byte) {
    char c = (char)byte;

    switch (p->state) {
        case ADV_STATE_IDLE:
            if (c == '+') {
                p->state = ADV_STATE_PREFIX;
                p->prefix_idx = 0;
            }
            break;

        case ADV_STATE_PREFIX:
            if ("IPD,"[p->prefix_idx] == c) {
                p->prefix_idx++;
                if (p->prefix_idx == 4) {
                    p->state = p->is_multilink ? ADV_STATE_LINK_ID : ADV_STATE_LEN;
                    p->len = 0;
                    p->link_id = 0;
                    p->comma_count = 0;
                }
            } else {
                p->state = ADV_STATE_IDLE;
            }
            break;

        case ADV_STATE_LINK_ID:
            if (c >= '0' && c <= '9') {
                p->link_id = p->link_id * 10 + (c - '0');
            } else if (c == ',') {
                p->state = ADV_STATE_LEN;
            } else {
                p->state = ADV_STATE_IDLE;
            }
            break;

        case ADV_STATE_LEN:
            if (c >= '0' && c <= '9') {
                p->len = p->len * 10 + (c - '0');
            } else if (c == ',') {
                // Якщо увімкнено CIPDINFO=1, пропуск IP та порту
                if (p->cipdinfo_enabled) {
                    p->state = ADV_STATE_SKIP_INFO;
                } else {
                    p->state = ADV_STATE_IDLE;
                }
            } else if (c == ':') {
                p->read_bytes = 0;
                if (p->len == 0) {
                    // Обробка крайового випадку кадру порожньої довжини len=0
                    p->state = ADV_STATE_IDLE;
                } else {
                    p->state = ADV_STATE_PAYLOAD;
                }
            } else {
                p->state = ADV_STATE_IDLE;
            }
            break;

        case ADV_STATE_SKIP_INFO:
            // Пропуск параметрів IP-адреси та порту до зустрічі двокрапки
            if (c == ':') {
                p->read_bytes = 0;
                p->state = (p->len == 0) ? ADV_STATE_IDLE : ADV_STATE_PAYLOAD;
            }
            break;

        case ADV_STATE_PAYLOAD:
            if (p->read_bytes < sizeof(p->payload)) {
                p->payload[p->read_bytes++] = byte;
            }
            if (p->read_bytes >= p->len) {
                // Завершення обробки кадру та негайна готовність до нового кадру
                p->state = ADV_STATE_IDLE;
            }
            break;
    }
}

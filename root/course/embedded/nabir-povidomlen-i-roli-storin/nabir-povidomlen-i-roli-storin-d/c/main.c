#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Бітові прапорці протокольного заголовка */
#define PROTO_FLAG_ACK_REQ   (1u << 0)
#define PROTO_FLAG_IS_RESP   (1u << 1)
#define PROTO_FLAG_IS_ERR    (1u << 2)
#define PROTO_FLAG_EXT_ADDR  (1u << 3)
#define PROTO_VERSION_1      (1u << 4)

/* Стандартні протокольні коди помилок */
typedef enum {
    ERR_OK              = 0x00,
    ERR_INVALID_PARAM   = 0x01,
    ERR_NOT_SUPPORTED   = 0x02,
    ERR_BUSY            = 0x03,
    ERR_INVALID_STATE   = 0x04,
    ERR_HARDWARE_FAULT  = 0x05,
    ERR_BUFFER_OVERFLOW = 0x06
} proto_err_t;

/* Ідентифікатори типів повідомлень */
typedef enum {
    MSG_CMD_PING            = 0x01,
    MSG_CMD_GET_TELEMETRY   = 0x10,
    MSG_CMD_SET_REPORT_RATE = 0x20,
    MSG_CMD_CALIBRATE_ADC   = 0x30
} msg_type_t;

/* Структура бінарного заголовка пакета (8 байтів) */
#pragma pack(push, 1)
typedef struct {
    uint8_t  msg_type;
    uint8_t  flags;
    uint8_t  trans_id;
    uint8_t  src_addr;
    uint8_t  dst_addr;
    uint16_t payload_len;
    uint8_t  reserved;
} proto_header_t;

/* Структури корисного навантаження */
typedef struct {
    int16_t  temperature_c_x10; /* Температура в 0.1 °C */
    uint32_t pressure_pa;        /* Тиск у Паскалях */
    uint8_t  battery_percent;    /* Заряд батареї 0..100% */
} telemetry_payload_t;

typedef struct {
    uint16_t rate_ms;           /* Період опитування 100..10000 мс */
} report_rate_payload_t;
#pragma pack(pop)

/* Сигнатура функції-обробника команди */
typedef proto_err_t (*cmd_handler_fn)(const uint8_t *req_payload, uint16_t req_len,
                                      uint8_t *resp_payload, uint16_t *resp_len,
                                      uint16_t max_resp_len);

/* Дескриптор маршруту в таблиці диспетчера */
typedef struct {
    uint8_t        msg_type;
    uint16_t       min_req_len;
    cmd_handler_fn handler;
} dispatch_entry_t;

/* Стан вузла */
static uint16_t g_report_rate_ms = 1000;
static bool g_is_calibrating = false;

/* 1. Обробник PING */
static proto_err_t handle_ping(const uint8_t *req, uint16_t req_len,
                               uint8_t *resp, uint16_t *resp_len, uint16_t max_resp) {
    (void)req; (void)req_len; (void)resp; (void)max_resp;
    *resp_len = 0;
    return ERR_OK;
}

/* 2. Обробник GET_TELEMETRY */
static proto_err_t handle_get_telemetry(const uint8_t *req, uint16_t req_len,
                                        uint8_t *resp, uint16_t *resp_len, uint16_t max_resp) {
    (void)req; (void)req_len;
    if (max_resp < sizeof(telemetry_payload_t)) {
        return ERR_BUFFER_OVERFLOW;
    }

    telemetry_payload_t *telem = (telemetry_payload_t *)resp;
    telem->temperature_c_x10 = 245;       /* 24.5 °C */
    telem->pressure_pa = 101325;          /* 1 атм */
    telem->battery_percent = 92;

    *resp_len = (uint16_t)sizeof(telemetry_payload_t);
    return ERR_OK;
}

/* 3. Обробник SET_REPORT_RATE */
static proto_err_t handle_set_report_rate(const uint8_t *req, uint16_t req_len,
                                          uint8_t *resp, uint16_t *resp_len, uint16_t max_resp) {
    (void)resp; (void)max_resp;
    if (req_len < sizeof(report_rate_payload_t)) {
        return ERR_INVALID_PARAM;
    }

    const report_rate_payload_t *cfg = (const report_rate_payload_t *)req;
    if (cfg->rate_ms < 100 || cfg->rate_ms > 10000) {
        return ERR_INVALID_PARAM; /* Вихід за допустимі межі */
    }

    g_report_rate_ms = cfg->rate_ms;
    *resp_len = 0;
    return ERR_OK;
}

/* 4. Обробник CALIBRATE_ADC */
static proto_err_t handle_calibrate_adc(const uint8_t *req, uint16_t req_len,
                                        uint8_t *resp, uint16_t *resp_len, uint16_t max_resp) {
    (void)req; (void)req_len; (void)resp; (void)max_resp;
    if (g_is_calibrating) {
        return ERR_BUSY; /* АЦП уже зайнятий калібруванням */
    }

    g_is_calibrating = true;
    /* Запуск апаратного автокалібрування... */
    *resp_len = 0;
    return ERR_OK;
}

/* Таблиця диспетчеризації */
static const dispatch_entry_t DISPATCH_TABLE[] = {
    { MSG_CMD_PING,            0, handle_ping },
    { MSG_CMD_GET_TELEMETRY,   0, handle_get_telemetry },
    { MSG_CMD_SET_REPORT_RATE, sizeof(report_rate_payload_t), handle_set_report_rate },
    { MSG_CMD_CALIBRATE_ADC,   0, handle_calibrate_adc }
};
#define DISPATCH_TABLE_SIZE (sizeof(DISPATCH_TABLE) / sizeof(DISPATCH_TABLE[0]))

/* Головна функція диспетчеризації вхідного пакета */
uint16_t proto_process_frame(const uint8_t *rx_buf, uint16_t rx_len,
                             uint8_t my_node_addr,
                             uint8_t *tx_buf, uint16_t max_tx_len) {
    if (rx_len < sizeof(proto_header_t)) {
        return 0; /* Кадр коротший за заголовок — відкидаємо */
    }

    const proto_header_t *rx_hdr = (const proto_header_t *)rx_buf;

    /* Фільтрація за адресою призначення (своя адреса або Broadcast) */
    if (rx_hdr->dst_addr != my_node_addr && rx_hdr->dst_addr != 0x00) {
        return 0; /* Чужий пакет */
    }

    /* Якщо це відповідь на наш попередній запит — віддаємо клієнтській черзі */
    if (rx_hdr->flags & PROTO_FLAG_IS_RESP) {
        /* Обробка вхідної відповіді клієнтом... */
        return 0;
    }

    /* Перевірка вимоги підтвердження (на широкомовні пакети не відповідаємо) */
    bool need_resp = (rx_hdr->flags & PROTO_FLAG_ACK_REQ) && (rx_hdr->dst_addr != 0x00);
    if (!need_resp) {
        /* Виконання команди без формування відповіді */
        for (size_t i = 0; i < DISPATCH_TABLE_SIZE; ++i) {
            if (DISPATCH_TABLE[i].msg_type == rx_hdr->msg_type) {
                uint16_t dummy_len = 0;
                DISPATCH_TABLE[i].handler(rx_buf + sizeof(proto_header_t), rx_hdr->payload_len,
                                          NULL, &dummy_len, 0);
                break;
            }
        }
        return 0;
    }

    if (max_tx_len < sizeof(proto_header_t) + 1) {
        return 0; /* Немає місця під вихідний буфер */
    }

    proto_header_t *tx_hdr = (proto_header_t *)tx_buf;
    tx_hdr->msg_type = rx_hdr->msg_type;
    tx_hdr->trans_id = rx_hdr->trans_id;
    tx_hdr->src_addr = my_node_addr;
    tx_hdr->dst_addr = rx_hdr->src_addr;
    tx_hdr->reserved = 0;

    uint8_t *tx_payload = tx_buf + sizeof(proto_header_t);
    uint16_t max_payload = max_tx_len - sizeof(proto_header_t);
    uint16_t out_payload_len = 0;

    /* Пошук обробника в таблиці маршрутизації */
    const dispatch_entry_t *entry = NULL;
    for (size_t i = 0; i < DISPATCH_TABLE_SIZE; ++i) {
        if (DISPATCH_TABLE[i].msg_type == rx_hdr->msg_type) {
            entry = &DISPATCH_TABLE[i];
            break;
        }
    }

    if (!entry) {
        /* Команда не підтримується */
        tx_hdr->flags = PROTO_FLAG_IS_RESP | PROTO_FLAG_IS_ERR | PROTO_VERSION_1;
        tx_payload[0] = (uint8_t)ERR_NOT_SUPPORTED;
        tx_hdr->payload_len = 1;
        return sizeof(proto_header_t) + 1;
    }

    /* Перевірка мінімальної довжини аргументів */
    if (rx_hdr->payload_len < entry->min_req_len) {
        tx_hdr->flags = PROTO_FLAG_IS_RESP | PROTO_FLAG_IS_ERR | PROTO_VERSION_1;
        tx_payload[0] = (uint8_t)ERR_INVALID_PARAM;
        tx_hdr->payload_len = 1;
        return sizeof(proto_header_t) + 1;
    }

    /* Виклик обробника */
    const uint8_t *rx_payload = rx_buf + sizeof(proto_header_t);
    proto_err_t status = entry->handler(rx_payload, rx_hdr->payload_len,
                                        tx_payload, &out_payload_len, max_payload);

    if (status == ERR_OK) {
        tx_hdr->flags = PROTO_FLAG_IS_RESP | PROTO_VERSION_1;
        tx_hdr->payload_len = out_payload_len;
        return sizeof(proto_header_t) + out_payload_len;
    } else {
        /* Обробник повернув код помилки */
        tx_hdr->flags = PROTO_FLAG_IS_RESP | PROTO_FLAG_IS_ERR | PROTO_VERSION_1;
        tx_payload[0] = (uint8_t)status;
        tx_hdr->payload_len = 1;
        return sizeof(proto_header_t) + 1;
    }
}

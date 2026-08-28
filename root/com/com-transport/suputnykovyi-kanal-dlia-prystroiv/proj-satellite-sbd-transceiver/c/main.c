#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define IRIDIUM_MAX_MO_LEN       340
#define IRIDIUM_MAX_MT_LEN       270
#define IRIDIUM_UART_TIMEOUT_MS  60000

typedef enum {
    IRIDIUM_OK = 0,
    IRIDIUM_ERR_TIMEOUT,
    IRIDIUM_ERR_CHECKSUM,
    IRIDIUM_ERR_NO_NETWORK,
    IRIDIUM_ERR_BUFFER_OVERFLOW,
    IRIDIUM_ERR_PROTOCOL
} iridium_err_t;

typedef struct {
    uint16_t mo_status;
    uint16_t momsn;
    uint16_t mt_status;
    uint16_t mtmsn;
    uint16_t mt_len;
    uint16_t mt_queued;
} sbdix_response_t;

/* Інтерфейс апаратного рівня (HAL) */
typedef struct {
    void (*set_power_pin)(bool state);
    void (*delay_ms)(uint32_t ms);
    int (*uart_write)(const uint8_t *data, size_t len);
    int (*uart_read_line)(char *buf, size_t max_len, uint32_t timeout_ms);
    int (*uart_read_bytes)(uint8_t *buf, size_t len, uint32_t timeout_ms);
} iridium_hal_t;

typedef struct {
    const iridium_hal_t *hal;
    bool is_powered;
} iridium_driver_t;

/* 16-бітна сума байтів за специфікацією Iridium SBD */
static uint16_t compute_checksum(const uint8_t *data, size_t len) {
    uint16_t sum = 0;
    for (size_t i = 0; i < len; ++i) {
        sum = (uint16_t)(sum + data[i]);
    }
    return sum;
}

iridium_err_t iridium_init(iridium_driver_t *dev, const iridium_hal_t *hal) {
    if (!dev || !hal) return IRIDIUM_ERR_PROTOCOL;
    dev->hal = hal;
    dev->is_powered = false;
    return IRIDIUM_OK;
}

iridium_err_t iridium_power_on(iridium_driver_t *dev) {
    dev->hal->set_power_pin(true);
    /* Пауза для заряду суперконденсаторів та завантаження DSP модуля */
    dev->hal->delay_ms(2000);
    dev->is_powered = true;

    /* Синхронізація швидкості UART */
    char resp[32];
    dev->hal->uart_write((const uint8_t *)"AT\r", 3);
    if (dev->hal->uart_read_line(resp, sizeof(resp), 2000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    return IRIDIUM_OK;
}

void iridium_power_off(iridium_driver_t *dev) {
    dev->hal->set_power_pin(false);
    dev->is_powered = false;
}

iridium_err_t iridium_get_signal_quality(iridium_driver_t *dev, uint8_t *csq_out) {
    char resp[32];
    dev->hal->uart_write((const uint8_t *)"AT+CSQ\r", 7);
    if (dev->hal->uart_read_line(resp, sizeof(resp), 3000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }

    int csq = 0;
    if (sscanf(resp, "+CSQ:%d", &csq) == 1) {
        *csq_out = (uint8_t)csq;
        return IRIDIUM_OK;
    }
    return IRIDIUM_ERR_PROTOCOL;
}

iridium_err_t iridium_load_binary_payload(iridium_driver_t *dev, const uint8_t *payload, size_t len) {
    if (len == 0 || len > IRIDIUM_MAX_MO_LEN) {
        return IRIDIUM_ERR_BUFFER_OVERFLOW;
    }

    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+SBDWB=%zu\r", len);
    dev->hal->uart_write((const uint8_t *)cmd, strlen(cmd));

    char resp[16];
    if (dev->hal->uart_read_line(resp, sizeof(resp), 2000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    if (strstr(resp, "READY") == NULL) {
        return IRIDIUM_ERR_PROTOCOL;
    }

    /* Відправка навантаження */
    dev->hal->uart_write(payload, len);

    /* Відправка 16-бітної чексуми Big-Endian */
    uint16_t checksum = compute_checksum(payload, len);
    uint8_t cs_bytes[2];
    cs_bytes[0] = (uint8_t)((checksum >> 8) & 0xFF);
    cs_bytes[1] = (uint8_t)(checksum & 0xFF);
    dev->hal->uart_write(cs_bytes, 2);

    /* Модем відповідає двійковим статусом '0' (OK) */
    if (dev->hal->uart_read_line(resp, sizeof(resp), 5000) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    if (resp[0] != '0') {
        return IRIDIUM_ERR_CHECKSUM;
    }
    return IRIDIUM_OK;
}

iridium_err_t iridium_send_sbd_session(iridium_driver_t *dev, sbdix_response_t *result) {
    dev->hal->uart_write((const uint8_t *)"AT+SBDIX\r", 9);

    char resp[96];
    /* Сесія з супутником може тривати до 60 секунд */
    if (dev->hal->uart_read_line(resp, sizeof(resp), IRIDIUM_UART_TIMEOUT_MS) <= 0) {
        return IRIDIUM_ERR_TIMEOUT;
    }

    int mo_st, momsn, mt_st, mtmsn, mt_len, mt_q;
    if (sscanf(resp, "+SBDIX: %d, %d, %d, %d, %d, %d",
               &mo_st, &momsn, &mt_st, &mtmsn, &mt_len, &mt_q) == 6) {
        result->mo_status = (uint16_t)mo_st;
        result->momsn = (uint16_t)momsn;
        result->mt_status = (uint16_t)mt_st;
        result->mtmsn = (uint16_t)mtmsn;
        result->mt_len = (uint16_t)mt_len;
        result->mt_queued = (uint16_t)mt_q;

        if (result->mo_status <= 4) {
            return IRIDIUM_OK;
        } else if (result->mo_status == 32) {
            return IRIDIUM_ERR_NO_NETWORK;
        }
        return IRIDIUM_ERR_PROTOCOL;
    }
    return IRIDIUM_ERR_PROTOCOL;
}

iridium_err_t iridium_read_binary_payload(iridium_driver_t *dev, uint8_t *buf, size_t *out_len, size_t max_len) {
    dev->hal->uart_write((const uint8_t *)"AT+SBDRB\r", 9);

    /* Зчитування 2 байтів довжини */
    uint8_t len_bytes[2];
    if (dev->hal->uart_read_bytes(len_bytes, 2, 3000) != 2) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    uint16_t payload_len = (uint16_t)((len_bytes[0] << 8) | len_bytes[1]);
    if (payload_len > max_len || payload_len > IRIDIUM_MAX_MT_LEN) {
        return IRIDIUM_ERR_BUFFER_OVERFLOW;
    }

    /* Зчитування самого навантаження */
    if (dev->hal->uart_read_bytes(buf, payload_len, 5000) != (int)payload_len) {
        return IRIDIUM_ERR_TIMEOUT;
    }

    /* Зчитування 2 байтів чексуми */
    uint8_t cs_bytes[2];
    if (dev->hal->uart_read_bytes(cs_bytes, 2, 2000) != 2) {
        return IRIDIUM_ERR_TIMEOUT;
    }
    uint16_t received_cs = (uint16_t)((cs_bytes[0] << 8) | cs_bytes[1]);
    uint16_t computed_cs = compute_checksum(buf, payload_len);

    if (received_cs != computed_cs) {
        return IRIDIUM_ERR_CHECKSUM;
    }

    *out_len = payload_len;
    return IRIDIUM_OK;
}

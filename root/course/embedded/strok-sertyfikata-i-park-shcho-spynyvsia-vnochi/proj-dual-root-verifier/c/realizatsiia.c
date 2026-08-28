#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"

#define TRUST_SLOT_MAGIC 0x54525553U
#define MAX_CERT_SIZE    2048U

typedef enum {
    SLOT_EMPTY   = 0xFF,
    SLOT_STANDBY = 0x02,
    SLOT_ACTIVE  = 0x01,
    SLOT_REVOKED = 0x00
} trust_slot_state_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t version;
    uint8_t  slot_state;
    uint8_t  reserved;
    uint32_t cert_len;
    uint64_t valid_from;
    uint64_t valid_to;
    uint32_t data_crc32;
    uint8_t  padding[36];
} trust_slot_header_t;

typedef struct {
    trust_slot_header_t header;
    uint8_t cert_data[MAX_CERT_SIZE];
} trust_slot_t;

typedef struct {
    mbedtls_x509_crt ca_chain;
    uint32_t active_certs_count;
    uint64_t current_system_time;
} dual_trust_store_t;

static uint32_t calculate_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

int dual_trust_store_init(dual_trust_store_t *store, uint64_t current_time) {
    if (!store) return -1;
    mbedtls_x509_crt_init(&store->ca_chain);
    store->active_certs_count = 0;
    store->current_system_time = current_time;
    return 0;
}

int dual_trust_store_load_slot(dual_trust_store_t *store, const trust_slot_t *slot) {
    if (!store || !slot) return -1;
    if (slot->header.magic != TRUST_SLOT_MAGIC) return -2;
    if (slot->header.slot_state != SLOT_ACTIVE && slot->header.slot_state != SLOT_STANDBY) {
        return -3;
    }
    if (slot->header.cert_len == 0 || slot->header.cert_len > MAX_CERT_SIZE) {
        return -4;
    }

    uint32_t calculated_crc = calculate_crc32(slot->cert_data, slot->header.cert_len);
    if (calculated_crc != slot->header.data_crc32) {
        return -5; /* Помилка контрольної суми */
    }

    /* Перевірка часових меж сертифіката, якщо системний час валідний */
    if (store->current_system_time > 0) {
        if (store->current_system_time < slot->header.valid_from ||
            store->current_system_time > slot->header.valid_to) {
            /* Сертифікат прострочений, але якщо це резервний слот, ми можемо завантажити його для аналізу */
            if (slot->header.slot_state == SLOT_ACTIVE) {
                return -6; /* Активний сертифікат прострочено */
            }
        }
    }

    /* Парсинг та додавання сертифіката X.509 до ланцюга Mbed TLS */
    int ret = mbedtls_x509_crt_parse(&store->ca_chain, slot->cert_data, slot->header.cert_len);
    if (ret != 0) {
        return ret;
    }

    store->active_certs_count++;
    return 0;
}

void dual_trust_store_free(dual_trust_store_t *store) {
    if (store) {
        mbedtls_x509_crt_free(&store->ca_chain);
        store->active_certs_count = 0;
    }
}

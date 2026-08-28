/* quota_enclave.h — Ядро квотованого провізіонування на C */
#ifndef QUOTA_ENCLAVE_H
#define QUOTA_ENCLAVE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CRYPTO_SIGNATURE_LEN 64
#define CRYPTO_PUBKEY_LEN    32
#define SILICON_UID_LEN      12
#define AUDIT_LOG_CAPACITY   1024

typedef enum {
    PROV_OK = 0,
    PROV_ERR_INVALID_SIGNATURE,
    PROV_ERR_EXPIRED,
    PROV_ERR_WRONG_STATION,
    PROV_ERR_QUOTA_EXHAUSTED,
    PROV_ERR_NVRAM_FAIL,
    PROV_ERR_INVALID_ARG
} prov_status_t;

/* Структура виробничого квитка замовника (OEM Ticket) */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic;                    /* Магічне число 'TKET' (0x544B4554) */
    uint32_t batch_id;                 /* Ідентифікатор партії */
    uint32_t model_id;                 /* Код моделі виробу */
    uint32_t station_id;               /* Номер авторизованого стенда */
    uint32_t quota_total;              /* Дозволений ліміт пристроїв */
    uint64_t valid_from_ts;            /* Початок часового вікна (UNIX timestamp) */
    uint64_t valid_until_ts;           /* Кінець часового вікна */
    uint8_t  oem_signature[CRYPTO_SIGNATURE_LEN]; /* Підпис OEM над полями вище */
} oem_ticket_t;

/* Запис журналу аудиту */
typedef struct {
    uint32_t record_seq;
    uint32_t batch_id;
    uint8_t  silicon_uid[SILICON_UID_LEN];
    uint8_t  device_pubkey[CRYPTO_PUBKEY_LEN];
    uint64_t timestamp;
} audit_record_t;
#pragma pack(pop)

/* Стан енергонезалежного лічильника та сесії станції */
typedef struct {
    uint32_t station_id;
    uint32_t active_batch_id;
    uint32_t quota_remaining;
    uint32_t total_issued;
    uint8_t  oem_root_pubkey[CRYPTO_PUBKEY_LEN];
    audit_record_t audit_log[AUDIT_LOG_CAPACITY];
    size_t   audit_count;
} enclave_context_t;

/* Заглушки криптографічних примітивів (у реальній системі — виклики PSA/mbedTLS/libsodium) */
bool crypto_verify_oem_signature(const uint8_t *data, size_t len,
                                 const uint8_t *sig, const uint8_t *pubkey);
bool crypto_sign_device_cert(const uint8_t *uid, const uint8_t *pubkey,
                             uint8_t *out_cert, size_t *out_cert_len);

/* Публічний API анклаву */
void enclave_init(enclave_context_t *ctx, uint32_t station_id, const uint8_t *oem_root_pubkey);
prov_status_t enclave_load_ticket(enclave_context_t *ctx, const oem_ticket_t *ticket, uint64_t current_ts);
prov_status_t enclave_provision_device(enclave_context_t *ctx,
                                       const uint8_t *silicon_uid,
                                       const uint8_t *device_pubkey,
                                       uint64_t current_ts,
                                       uint8_t *out_cert,
                                       size_t *out_cert_len);

#endif /* QUOTA_ENCLAVE_H */

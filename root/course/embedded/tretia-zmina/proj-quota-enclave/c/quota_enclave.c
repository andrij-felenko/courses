/* quota_enclave.c — Реалізація безпечного лічильника та видачі на C */
#include "quota_enclave.h"
#include <string.h>

#define TICKET_MAGIC 0x544B4554  /* 'TKET' */

/* Імітація криптографічної перевірки підпису OEM */
bool crypto_verify_oem_signature(const uint8_t *data, size_t len,
                                 const uint8_t *sig, const uint8_t *pubkey) {
    (void)data; (void)len; (void)sig; (void)pubkey;
    /* У бойовому модулі: ed25519_verify(sig, data, len, pubkey) == 0 */
    return true;
}

/* Імітація випуску сертифіката плати заводським ключем */
bool crypto_sign_device_cert(const uint8_t *uid, const uint8_t *pubkey,
                             uint8_t *out_cert, size_t *out_cert_len) {
    if (!uid || !pubkey || !out_cert || !out_cert_len) return false;
    /* Формуємо структуру сертифіката: UID + PubKey + мітка */
    memcpy(out_cert, uid, SILICON_UID_LEN);
    memcpy(out_cert + SILICON_UID_LEN, pubkey, CRYPTO_PUBKEY_LEN);
    *out_cert_len = SILICON_UID_LEN + CRYPTO_PUBKEY_LEN;
    return true;
}

/* Атомарне оновлення енергонезалежного лічильника квоти */
static bool nvram_atomic_decrement(uint32_t *quota_var) {
    if (*quota_var == 0) return false;
    /* У реальному залізі: запис нового значення в OTP-блок або флеш-банк зі статусом */
    (*quota_var)--;
    return true;
}

void enclave_init(enclave_context_t *ctx, uint32_t station_id, const uint8_t *oem_root_pubkey) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(enclave_context_t));
    ctx->station_id = station_id;
    if (oem_root_pubkey) {
        memcpy(ctx->oem_root_pubkey, oem_root_pubkey, CRYPTO_PUBKEY_LEN);
    }
}

prov_status_t enclave_load_ticket(enclave_context_t *ctx, const oem_ticket_t *ticket, uint64_t current_ts) {
    if (!ctx || !ticket) return PROV_ERR_INVALID_ARG;

    if (ticket->magic != TICKET_MAGIC) return PROV_ERR_INVALID_ARG;
    if (ticket->station_id != ctx->station_id) return PROV_ERR_WRONG_STATION;
    if (current_ts < ticket->valid_from_ts || current_ts > ticket->valid_until_ts) {
        return PROV_ERR_EXPIRED;
    }

    /* Довжина підписаної частини: уся структура без поля oem_signature */
    size_t signed_len = offsetof(oem_ticket_t, oem_signature);
    bool sig_ok = crypto_verify_oem_signature((const uint8_t *)ticket, signed_len,
                                              ticket->oem_signature, ctx->oem_root_pubkey);
    if (!sig_ok) {
        return PROV_ERR_INVALID_SIGNATURE;
    }

    /* Активація квоти партії */
    ctx->active_batch_id = ticket->batch_id;
    ctx->quota_remaining = ticket->quota_total;
    ctx->total_issued = 0;
    ctx->audit_count = 0;

    return PROV_OK;
}

prov_status_t enclave_provision_device(enclave_context_t *ctx,
                                       const uint8_t *silicon_uid,
                                       const uint8_t *device_pubkey,
                                       uint64_t current_ts,
                                       uint8_t *out_cert,
                                       size_t *out_cert_len) {
    if (!ctx || !silicon_uid || !device_pubkey || !out_cert || !out_cert_len) {
        return PROV_ERR_INVALID_ARG;
    }

    /* 1. Залізна перевірка квоти */
    if (ctx->quota_remaining == 0) {
        return PROV_ERR_QUOTA_EXHAUSTED;
    }

    /* 2. Атомарне списання ліміту ПЕРЕД створенням артефакту */
    if (!nvram_atomic_decrement(&ctx->quota_remaining)) {
        return PROV_ERR_NVRAM_FAIL;
    }

    /* 3. Генерація цифрового підпису та сертифіката */
    if (!crypto_sign_device_cert(silicon_uid, device_pubkey, out_cert, out_cert_len)) {
        /* При відмові підпису квота вже списана: це захищає від атак перебору */
        return PROV_ERR_NVRAM_FAIL;
    }

    /* 4. Запис у журнал аудиту */
    if (ctx->audit_count < AUDIT_LOG_CAPACITY) {
        audit_record_t *rec = &ctx->audit_log[ctx->audit_count++];
        rec->record_seq = ctx->total_issued + 1;
        rec->batch_id = ctx->active_batch_id;
        rec->timestamp = current_ts;
        memcpy(rec->silicon_uid, silicon_uid, SILICON_UID_LEN);
        memcpy(rec->device_pubkey, device_pubkey, CRYPTO_PUBKEY_LEN);
    }

    ctx->total_issued++;
    return PROV_OK;
}

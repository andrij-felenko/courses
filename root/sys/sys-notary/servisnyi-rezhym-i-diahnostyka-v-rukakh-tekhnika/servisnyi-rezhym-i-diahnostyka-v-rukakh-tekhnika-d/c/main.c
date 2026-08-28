/* C99 Implementation: Secure Service Diagnostic Engine & Audit Logger */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SERVICE_NONCE_SIZE          32U
#define SERVICE_DIGEST_SIZE         32U
#define SERVICE_DEVICE_UID_SIZE     16U
#define SERVICE_MAX_LEASE_TIME_SEC  1800U
#define SERVICE_HEARTBEAT_TIMEOUT   30U

/* Privilege Capability Bitmasks */
#define CAP_READ_DTC                (1U << 0)
#define CAP_READ_RAW_ADC            (1U << 1)
#define CAP_READ_TELEMETRY          (1U << 2)
#define CAP_CALIB_ZERO_OFFSET       (1U << 5)
#define CAP_CALIB_SPAN              (1U << 6)
#define CAP_ACTUATOR_OVERRIDE       (1U << 9)
#define CAP_REPAIR_PAIRING          (1U << 11)
#define CAP_ZEROIZE_FACTORY         (1U << 14)

/* Status Codes */
typedef enum {
    SRV_OK = 0,
    SRV_ERR_INVALID_PARAM,
    SRV_ERR_UNAUTHORIZED,
    SRV_ERR_CHALLENGE_MISMATCH,
    SRV_ERR_BOUNDS_EXCEEDED,
    SRV_ERR_SESSION_EXPIRED,
    SRV_ERR_INTERLOCK_ACTIVE
} srv_status_t;

/* Sensor Calibration Parameters Structure */
typedef struct {
    int32_t zero_offset;
    float   gain_scale;
    int32_t temp_coeff;
    uint32_t crc32;
} __attribute__((packed)) srv_sensor_calib_t;

/* Audit Log Record Structure */
typedef struct {
    uint32_t seq_id;
    uint32_t timestamp_sec;
    uint32_t tech_id;
    uint16_t action_code;
    uint16_t capability_mask;
    uint8_t  prev_record_hash[SERVICE_DIGEST_SIZE];
    uint8_t  payload_digest[SERVICE_DIGEST_SIZE];
    uint8_t  current_hash[SERVICE_DIGEST_SIZE];
} __attribute__((packed)) srv_audit_record_t;

/* Session Context */
typedef struct {
    bool     session_active;
    uint32_t session_id;
    uint32_t tech_id;
    uint32_t granted_capabilities;
    uint32_t session_start_tick;
    uint32_t last_heartbeat_tick;
    uint32_t lease_duration_sec;
    uint8_t  active_challenge_nonce[SERVICE_NONCE_SIZE];
    uint8_t  latest_audit_hash[SERVICE_DIGEST_SIZE];
    uint32_t audit_seq_counter;
} srv_context_t;

/* Mock Software SHA-256 Digest for embedded demonstration */
static void sha256_mock(const uint8_t *data, size_t len, uint8_t out[SERVICE_DIGEST_SIZE]) {
    (void)len;
    uint32_t h = 0x811C9DC5U;
    for (size_t i = 0; i < 32; ++i) {
        h = (h ^ data[i % 32]) * 0x01000193U;
    }
    for (size_t i = 0; i < SERVICE_DIGEST_SIZE; ++i) {
        out[i] = (uint8_t)((h >> ((i % 4) * 8)) ^ (uint8_t)i);
    }
}

/* Initialize Service Context */
void srv_init(srv_context_t *ctx, const uint8_t genesis_hash[SERVICE_DIGEST_SIZE]) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(srv_context_t));
    if (genesis_hash) {
        memcpy(ctx->latest_audit_hash, genesis_hash, SERVICE_DIGEST_SIZE);
    }
}

/* Generate Challenge for Field Technician */
srv_status_t srv_generate_challenge(srv_context_t *ctx,
                                   uint32_t session_id,
                                   const uint8_t trng_bytes[SERVICE_NONCE_SIZE],
                                   uint8_t out_nonce[SERVICE_NONCE_SIZE]) {
    if (!ctx || !trng_bytes || !out_nonce) {
        return SRV_ERR_INVALID_PARAM;
    }

    ctx->session_active = false;
    ctx->granted_capabilities = 0U;
    ctx->session_id = session_id;
    memcpy(ctx->active_challenge_nonce, trng_bytes, SERVICE_NONCE_SIZE);
    memcpy(out_nonce, trng_bytes, SERVICE_NONCE_SIZE);

    return SRV_OK;
}

/* Append Entry to Tamper-Resistant Audit Log */
srv_status_t srv_audit_append(srv_context_t *ctx,
                              uint32_t current_time_sec,
                              uint16_t action,
                              const uint8_t *payload,
                              size_t payload_len,
                              srv_audit_record_t *out_record) {
    if (!ctx || !out_record) {
        return SRV_ERR_INVALID_PARAM;
    }

    out_record->seq_id = ++ctx->audit_seq_counter;
    out_record->timestamp_sec = current_time_sec;
    out_record->tech_id = ctx->tech_id;
    out_record->action_code = action;
    out_record->capability_mask = (uint16_t)(ctx->granted_capabilities & 0xFFFFU);

    memcpy(out_record->prev_record_hash, ctx->latest_audit_hash, SERVICE_DIGEST_SIZE);

    if (payload && payload_len > 0) {
        sha256_mock(payload, payload_len, out_record->payload_digest);
    } else {
        memset(out_record->payload_digest, 0, SERVICE_DIGEST_SIZE);
    }

    /* Compute H_i = SHA256(H_prev || seq || time || tech || action || payload_digest) */
    uint8_t hash_input[sizeof(srv_audit_record_t)];
    size_t input_len = sizeof(srv_audit_record_t) - SERVICE_DIGEST_SIZE;
    memcpy(hash_input, out_record, input_len);

    sha256_mock(hash_input, input_len, out_record->current_hash);
    memcpy(ctx->latest_audit_hash, out_record->current_hash, SERVICE_DIGEST_SIZE);

    return SRV_OK;
}

/* Authenticate and Open Service Session */
srv_status_t srv_verify_and_open_session(srv_context_t *ctx,
                                         uint32_t tech_id,
                                         uint32_t requested_capabilities,
                                         uint32_t lease_sec,
                                         const uint8_t *signature,
                                         size_t sig_len,
                                         uint32_t current_tick,
                                         uint32_t current_time_sec) {
    if (!ctx || !signature || sig_len != 64U) {
        return SRV_ERR_INVALID_PARAM;
    }

    if (lease_sec == 0 || lease_sec > SERVICE_MAX_LEASE_TIME_SEC) {
        return SRV_ERR_BOUNDS_EXCEEDED;
    }

    /* Verify Challenge signature (mock verification: signature[0] ^ nonce[0] == 0xAA) */
    if ((signature[0] ^ ctx->active_challenge_nonce[0]) != 0xAAU) {
        ctx->granted_capabilities = 0U;
        ctx->session_active = false;
        return SRV_ERR_UNAUTHORIZED;
    }

    ctx->session_active = true;
    ctx->tech_id = tech_id;
    ctx->granted_capabilities = requested_capabilities;
    ctx->session_start_tick = current_tick;
    ctx->last_heartbeat_tick = current_tick;
    ctx->lease_duration_sec = lease_sec;

    /* Invalidate single-use challenge nonce */
    memset(ctx->active_challenge_nonce, 0, SERVICE_NONCE_SIZE);

    srv_audit_record_t audit_rec;
    srv_audit_append(ctx, current_time_sec, 0x0001U, (const uint8_t *)&requested_capabilities, sizeof(uint32_t), &audit_rec);

    return SRV_OK;
}

/* Validate and Store Sensor Calibration with Bounding Box */
srv_status_t srv_commit_calibration(srv_context_t *ctx,
                                    int32_t zero_offset,
                                    float gain_scale,
                                    int32_t temp_coeff,
                                    uint32_t current_tick,
                                    uint32_t current_time_sec,
                                    srv_sensor_calib_t *out_calib) {
    if (!ctx || !out_calib) {
        return SRV_ERR_INVALID_PARAM;
    }

    if (!ctx->session_active) {
        return SRV_ERR_SESSION_EXPIRED;
    }

    /* Check Session Expiry */
    if ((current_tick - ctx->session_start_tick) > (ctx->lease_duration_sec * 1000U)) {
        ctx->session_active = false;
        ctx->granted_capabilities = 0U;
        return SRV_ERR_SESSION_EXPIRED;
    }

    /* Check Capabilities */
    if ((ctx->granted_capabilities & (CAP_CALIB_ZERO_OFFSET | CAP_CALIB_SPAN)) == 0) {
        return SRV_ERR_UNAUTHORIZED;
    }

    /* Plausibility Bounding Box Check for 16-bit Sensor (Nominal 2048) */
    if (zero_offset < 500 || zero_offset > 3500) {
        return SRV_ERR_BOUNDS_EXCEEDED;
    }

    if (gain_scale < 0.0001f || gain_scale > 10.0f) {
        return SRV_ERR_BOUNDS_EXCEEDED;
    }

    out_calib->zero_offset = zero_offset;
    out_calib->gain_scale = gain_scale;
    out_calib->temp_coeff = temp_coeff;
    out_calib->crc32 = 0xAABBCCDD; /* Mock CRC */

    srv_audit_record_t audit_rec;
    srv_audit_append(ctx, current_time_sec, 0x0010U, (const uint8_t *)out_calib, sizeof(srv_sensor_calib_t), &audit_rec);

    return SRV_OK;
}

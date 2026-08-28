#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ALLOWED_FORCE_N      150.0f
#define MAX_ALLOWED_VELOCITY_MPS   1.2f
#define TOKEN_MAX_TTL_MS          300U
#define AUDIT_LOG_CAPACITY        128U

typedef enum {
    INTERLOCK_OK = 0,
    INTERLOCK_ERR_TOKEN_EXPIRED,
    INTERLOCK_ERR_TOKEN_INVALID_SIG,
    INTERLOCK_ERR_PERMISSION_DENIED,
    INTERLOCK_ERR_FORCE_LIMIT_EXCEEDED,
    INTERLOCK_ERR_VELOCITY_LIMIT_EXCEEDED,
    INTERLOCK_ERR_ESTOP_TRIGGERED,
    INTERLOCK_ERR_AUDIT_LOG_FULL
} InterlockStatus;

typedef enum {
    PERM_NONE           = 0x00,
    PERM_MOTION_ARM     = 0x01,
    PERM_TOOL_ACTIVATE  = 0x02,
    PERM_OVERRIDE_SPEED = 0x04
} PermissionFlags;

typedef struct {
    uint32_t operator_id;
    uint32_t permissions;
    uint64_t timestamp_ms;
    uint32_t ttl_ms;
    uint32_t signature_crc32;
} OperatorToken;

typedef struct {
    uint32_t action_id;
    uint32_t required_perm;
    float requested_force_n;
    float requested_velocity_mps;
    float ml_confidence;
    uint32_t model_weights_hash;
} ActuationProposal;

typedef struct {
    uint64_t log_timestamp_ms;
    uint32_t action_id;
    uint32_t operator_id;
    float applied_force_n;
    float ml_confidence;
    InterlockStatus status;
} AuditRecord;

typedef struct {
    AuditRecord records[AUDIT_LOG_CAPACITY];
    size_t count;
    bool estop_physical_state;
} SafetyInterlockState;

static uint32_t calc_token_crc(const OperatorToken *tok) {
    /* Простий апаратний CRC32 для ілюстрації цілісності пакета */
    uint32_t crc = 0xFFFFFFFFU;
    const uint8_t *data = (const uint8_t *)tok;
    size_t len = sizeof(OperatorToken) - sizeof(tok->signature_crc32);
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int b = 0; b < 8; ++b) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

void interlock_init(SafetyInterlockState *state) {
    memset(state, 0, sizeof(SafetyInterlockState));
    state->estop_physical_state = true;
}

InterlockStatus interlock_evaluate(
    SafetyInterlockState *state,
    const ActuationProposal *prop,
    const OperatorToken *tok,
    uint64_t current_time_ms,
    bool hardware_estop_pin_active
) {
    state->estop_physical_state = hardware_estop_pin_active;
    
    if (!hardware_estop_pin_active) {
        return INTERLOCK_ERR_ESTOP_TRIGGERED;
    }

    if (calc_token_crc(tok) != tok->signature_crc32) {
        return INTERLOCK_ERR_TOKEN_INVALID_SIG;
    }

    /* Беззнакова різниця захищає від переповнення монотонного таймера */
    uint64_t elapsed_ms = current_time_ms - tok->timestamp_ms;
    if (elapsed_ms > tok->ttl_ms || tok->ttl_ms > TOKEN_MAX_TTL_MS) {
        return INTERLOCK_ERR_TOKEN_EXPIRED;
    }

    if ((tok->permissions & prop->required_perm) != prop->required_perm) {
        return INTERLOCK_ERR_PERMISSION_DENIED;
    }

    if (prop->requested_force_n > MAX_ALLOWED_FORCE_N || prop->requested_force_n < 0.0f) {
        return INTERLOCK_ERR_FORCE_LIMIT_EXCEEDED;
    }

    if (prop->requested_velocity_mps > MAX_ALLOWED_VELOCITY_MPS || prop->requested_velocity_mps < 0.0f) {
        return INTERLOCK_ERR_VELOCITY_LIMIT_EXCEEDED;
    }

    if (state->count >= AUDIT_LOG_CAPACITY) {
        return INTERLOCK_ERR_AUDIT_LOG_FULL;
    }

    /* Атомарний запис аудиту ДО генерації сигналу керування */
    AuditRecord *rec = &state->records[state->count++];
    rec->log_timestamp_ms = current_time_ms;
    rec->action_id = prop->action_id;
    rec->operator_id = tok->operator_id;
    rec->applied_force_n = prop->requested_force_n;
    rec->ml_confidence = prop->ml_confidence;
    rec->status = INTERLOCK_OK;

    return INTERLOCK_OK;
}

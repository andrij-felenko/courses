#ifndef AUTH_PROTOCOL_H
#define AUTH_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

#define AUTH_MAGIC_BYTE            0xAA
#define AUTH_PROTO_VERSION         0x01

#define AUTH_HEARTBEAT_TIMEOUT_MS  1000
#define AUTH_HANDOVER_TIMEOUT_MS   5000
#define AUTH_DEADBAND_PERCENT       3.0f

typedef enum {
    AUTH_ROLE_NONE      = 0x00,
    AUTH_ROLE_MONITOR   = 0x01,
    AUTH_ROLE_PILOT     = 0x02,
    AUTH_ROLE_PAYLOAD   = 0x04,
    AUTH_ROLE_COMMANDER = 0x08
} auth_role_flags_t;

typedef enum {
    AUTH_STATUS_OK                  = 0x00,
    AUTH_ERR_UNAUTHORIZED          = 0x01,
    AUTH_ERR_TOKEN_ALREADY_TAKEN    = 0x02,
    AUTH_ERR_STICK_NOT_NEUTRAL      = 0x03,
    AUTH_ERR_LEASE_EXPIRED          = 0x04,
    AUTH_ERR_PRIORITY_TOO_LOW       = 0x05,
    AUTH_ERR_CRC_MISMATCH           = 0x06
} auth_status_code_t;

#pragma pack(push, 1)

/* Заголовок протоколу арбітражу (24 байти) */
typedef struct {
    uint8_t  magic;
    uint8_t  version;
    uint16_t msg_id;
    uint8_t  source_id;
    uint8_t  target_id;
    uint16_t seq_num;
    uint32_t timestamp_ms;
    uint32_t token_nonce;
    uint16_t payload_len;
    uint16_t crc16;
} auth_header_t;

/* MSG_AUTH_HEARTBEAT (0x0080) */
typedef struct {
    uint8_t  active_roles;
    uint16_t lease_requested_ms;
} msg_auth_heartbeat_t;

/* MSG_AUTH_TOKEN_REQ (0x0081) */
typedef struct {
    uint8_t  requested_role;
    uint8_t  target_gcs_id;
    uint32_t auth_token;
} msg_auth_token_req_t;

/* MSG_HANDOVER_STICK_CHECK (0x0085) */
typedef struct {
    int16_t roll_axis;      /* Нормалізований діапазон: -1000 .. +1000 */
    int16_t pitch_axis;     /* Нормалізований діапазон: -1000 .. +1000 */
    int16_t yaw_axis;       /* Нормалізований діапазон: -1000 .. +1000 */
    int16_t throttle_axis;  /* Нормалізований діапазон: 0 .. +1000 */
    uint8_t is_neutral;     /* 1 - у дедбенді, 0 - відхилено */
} msg_stick_check_t;

/* MSG_COMMANDER_OVERRIDE (0x0086) */
typedef struct {
    uint8_t  override_reason;
    uint8_t  action_command;
    uint32_t signature_hash;
} msg_commander_override_t;

/* MSG_AUTH_STATUS (0x0087) */
typedef struct {
    uint8_t  pilot_gcs_id;
    uint8_t  payload_gcs_id;
    uint8_t  commander_gcs_id;
    uint32_t pilot_lease_remaining_ms;
    uint8_t  arbitration_state;
} msg_auth_status_t;

#pragma pack(pop)

#endif /* AUTH_PROTOCOL_H */

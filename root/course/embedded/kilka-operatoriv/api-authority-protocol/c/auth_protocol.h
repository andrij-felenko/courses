#ifndef AUTH_PROTOCOL_H
#define AUTH_PROTOCOL_H

#include <stdint.h>
#include <stdbool.h>

/* Маркер синхронізації та версія бінарного формату (розділ 2). */
#define AUTH_MAGIC_BYTE             0xAAu
#define AUTH_PROTO_VERSION          0x01u

/* Широкомовна адреса: кадр адресовано всім учасникам мережі. */
#define AUTH_BROADCAST_ID           0xFFu

/* Часові вимоги розділу 4: серцебиття не рідше 250 мс, оренда 1000 мс,
   вікно звірки нейтралі при передачі зміни — 5000 мс. */
#define AUTH_HEARTBEAT_PERIOD_MS     250u
#define AUTH_LEASE_TIMEOUT_MS       1000u
#define AUTH_HANDOVER_TIMEOUT_MS    5000u

/* Осі стіків нормалізовано в ±1000, мертва зона ±3% — це ±30 одиниць. */
#define AUTH_AXIS_FULL_SCALE        1000
#define AUTH_DEADBAND_UNITS           30

typedef enum {
    AUTH_ROLE_NONE      = 0x00,
    AUTH_ROLE_MONITOR   = 0x01,
    AUTH_ROLE_PILOT     = 0x02,
    AUTH_ROLE_PAYLOAD   = 0x04,
    AUTH_ROLE_COMMANDER = 0x08
} auth_role_flags_t;

typedef enum {
    AUTH_STATUS_OK               = 0x00,
    AUTH_ERR_UNAUTHORIZED        = 0x01,
    AUTH_ERR_TOKEN_ALREADY_TAKEN = 0x02,
    AUTH_ERR_STICK_NOT_NEUTRAL   = 0x03,
    AUTH_ERR_LEASE_EXPIRED       = 0x04,
    AUTH_ERR_PRIORITY_TOO_LOW    = 0x05,
    AUTH_ERR_CRC_MISMATCH        = 0x06,
    /* Помилки рівня кадру: до розбору корисного навантаження. */
    AUTH_ERR_BAD_MAGIC           = 0x07,
    AUTH_ERR_BAD_VERSION         = 0x08,
    AUTH_ERR_BAD_LENGTH          = 0x09,
    AUTH_ERR_REPLAY              = 0x0A
} auth_status_code_t;

/* Ідентифікатори повідомлень (розділ 3). */
#define MSG_AUTH_HEARTBEAT          0x0080u
#define MSG_AUTH_TOKEN_REQ          0x0081u
#define MSG_AUTH_TOKEN_GRANT        0x0082u
#define MSG_AUTH_TOKEN_REVOKE       0x0083u
#define MSG_HANDOVER_OFFER          0x0084u
#define MSG_HANDOVER_STICK_CHECK    0x0085u
#define MSG_COMMANDER_OVERRIDE      0x0086u
#define MSG_AUTH_STATUS             0x0087u

/* Стани скінченного автомата арбітра (розділ 5). */
typedef enum {
    AUTH_STATE_IDLE                = 0,
    AUTH_STATE_PILOT_ACTIVE        = 1,
    AUTH_STATE_HANDOVER_WAIT_STICK = 2,
    AUTH_STATE_LINK_LOST           = 3,
    AUTH_STATE_COMMANDER_LOCKED    = 4
} auth_arb_state_t;

/* Що арбітр наказує зробити автопілоту, коли повноваження зникли. */
typedef enum {
    AUTH_FAILSAFE_NONE   = 0,
    AUTH_FAILSAFE_LOITER = 1,
    AUTH_FAILSAFE_RTL    = 2,
    AUTH_FAILSAFE_BRAKE  = 3
} auth_failsafe_t;

/* Причина, з якої борт відкликав токен. */
typedef enum {
    AUTH_REVOKE_LEASE_EXPIRED = 0,
    AUTH_REVOKE_HANDOVER      = 1,
    AUTH_REVOKE_COMMANDER     = 2
} auth_revoke_reason_t;

/* Дія, якої вимагає командир у MSG_COMMANDER_OVERRIDE. */
typedef enum {
    AUTH_OVERRIDE_HOLD    = 0,  /* зависання / BRAKE, токени анульовано */
    AUTH_OVERRIDE_RTL     = 1,  /* повернення на базу */
    AUTH_OVERRIDE_RELEASE = 2   /* зняти блокування, дозволити нові запити */
} auth_override_action_t;

#pragma pack(push, 1)

/* Заголовок кадру. На дроті — 20 байтів: рівно сума полів із діаграми
   розділу 2 (1+1+2 +1+1+2 +4 +4 +2+2). Порядок байтів Little-Endian;
   структура тут лише зручний контейнер, на дріт кладе auth_frame_encode. */
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

/* MSG_AUTH_TOKEN_REQ (0x0081).
   target_gcs_id != 0 у запиті ролі пілота від діючого пілота означає
   не захоплення токена, а ініціацію передачі зміни на вказану станцію. */
typedef struct {
    uint8_t  requested_role;
    uint8_t  target_gcs_id;
    uint32_t auth_token;
} msg_auth_token_req_t;

/* MSG_AUTH_TOKEN_GRANT (0x0082). Кадр несе і відмову: status != 0,
   granted_role == AUTH_ROLE_NONE. */
typedef struct {
    uint8_t  granted_role;
    uint8_t  status;
    uint16_t lease_ms;
    uint32_t token_nonce;
} msg_auth_token_grant_t;

/* MSG_AUTH_TOKEN_REVOKE (0x0083) */
typedef struct {
    uint8_t revoked_role;
    uint8_t reason;
    uint8_t gcs_id;
} msg_auth_token_revoke_t;

/* MSG_HANDOVER_OFFER (0x0084). throttle_target — поточний газ борту,
   під який змінний пілот вирівнює свій стік перед звіркою. */
typedef struct {
    uint8_t  from_gcs_id;
    uint8_t  to_gcs_id;
    uint16_t timeout_ms;
    int16_t  throttle_target;
} msg_handover_offer_t;

/* MSG_HANDOVER_STICK_CHECK (0x0085) */
typedef struct {
    int16_t roll_axis;      /* Нормалізований діапазон: -1000 .. +1000 */
    int16_t pitch_axis;     /* Нормалізований діапазон: -1000 .. +1000 */
    int16_t yaw_axis;       /* Нормалізований діапазон: -1000 .. +1000 */
    int16_t throttle_axis;  /* Нормалізований діапазон: 0 .. +1000 */
    uint8_t is_neutral;     /* Думка станції; борт усе одно рахує сам */
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

typedef struct __mavlink_message {
    uint16_t checksum;
    uint8_t  magic;              /* 0xFD для MAVLink 2, 0xFE для MAVLink 1 */
    uint8_t  len;                /* довжина корисних даних, можливо обрізаних */
    uint8_t  incompat_flags;
    uint8_t  compat_flags;
    uint8_t  seq;
    uint8_t  sysid;
    uint8_t  compid;
    uint32_t msgid:24;           /* 24 біти, як на дроті */
    uint64_t payload64[(MAVLINK_MAX_PAYLOAD_LEN + MAVLINK_NUM_CHECKSUM_BYTES + 7) / 8];
    uint8_t  ck[2];
    uint8_t  signature[MAVLINK_SIGNATURE_BLOCK_LEN];  /* 13 байтів */
} mavlink_message_t;

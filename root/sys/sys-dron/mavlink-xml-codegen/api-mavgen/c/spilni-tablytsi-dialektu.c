typedef struct __mavlink_msg_entry {
    uint32_t msgid;
    uint8_t  crc_extra;
    uint8_t  min_msg_len;          /* довжина базової частини */
    uint8_t  max_msg_len;          /* повна довжина з розширеннями */
    uint8_t  flags;                /* MAV_MSG_ENTRY_FLAG_* */
    uint8_t  target_system_ofs;    /* зміщення поля-адресата; чи воно є — каже flags */
    uint8_t  target_component_ofs;
} mavlink_msg_entry_t;

/* У common.h: суцільний список, упорядкований за визначником. */
#define MAVLINK_MESSAGE_CRCS {{0, 50, 9, 9, 0, 0, 0}, \
                              {1, 124, 31, 43, 0, 0, 0}, \
                              {2, 137, 12, 12, 0, 0, 0}, \
                              /* … */ {30, 39, 28, 28, 0, 0, 0}, /* … */}

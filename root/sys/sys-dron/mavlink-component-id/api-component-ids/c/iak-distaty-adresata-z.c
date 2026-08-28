typedef struct __mavlink_msg_entry {
    uint32_t msgid;
    uint8_t  crc_extra;
    uint8_t  min_msg_len;           /* без розширень MAVLink 2 */
    uint8_t  max_msg_len;           /* з розширеннями         */
    uint8_t  flags;                 /* MAV_MSG_ENTRY_FLAG_*   */
    uint8_t  target_system_ofs;     /* зсув у корисних даних, або 0 */
    uint8_t  target_component_ofs;  /* зсув у корисних даних, або 0 */
} mavlink_msg_entry_t;

#define MAV_MSG_ENTRY_FLAG_HAVE_TARGET_SYSTEM     1
#define MAV_MSG_ENTRY_FLAG_HAVE_TARGET_COMPONENT  2

const mavlink_msg_entry_t *mavlink_get_msg_entry(uint32_t msgid);

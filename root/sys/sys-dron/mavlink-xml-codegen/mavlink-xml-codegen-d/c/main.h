/* Згенеровано з common.xml — руками не правити. */
typedef struct __mavlink_attitude_t {
    uint32_t time_boot_ms;   /* зміщення 0 — 4-байтове поле попереду */
    float roll;              /* 4  */
    float pitch;             /* 8  */
    float yaw;               /* 12 */
    float rollspeed;         /* 16 */
    float pitchspeed;        /* 20 */
    float yawspeed;          /* 24 */
} mavlink_attitude_t;        /* усього 28 байтів */

#define MAVLINK_MSG_ID_ATTITUDE_CRC 39

/* Пакування у кадр: заповнює msg і рахує CRC разом із CRC_EXTRA. */
uint16_t mavlink_msg_attitude_pack(uint8_t sysid, uint8_t compid,
                                   mavlink_message_t *msg,
                                   uint32_t time_boot_ms,
                                   float roll, float pitch, float yaw,
                                   float rollspeed, float pitchspeed, float yawspeed);

/* Розпакування: розкладає корисні дані отриманого кадру по полях. */
void mavlink_msg_attitude_decode(const mavlink_message_t *msg,
                                 mavlink_attitude_t *attitude);

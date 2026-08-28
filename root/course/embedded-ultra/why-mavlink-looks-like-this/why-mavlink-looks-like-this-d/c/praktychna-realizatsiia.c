#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAVLINK_STX_V2 0xFD
#define MAVLINK_MSG_ID_ATTITUDE 30
#define MAVLINK_CRC_EXTRA_ATTITUDE 39

// Структура корисного навантаження ATTITUDE (28 байтів)
typedef struct __attribute__((packed)) {
    uint32_t time_boot_ms; // Час від завантаження [мс]
    float roll;            // Кут крену [рад] (-pi..+pi)
    float pitch;           // Кут тангажу [рад] (-pi..+pi)
    float yaw;             // Кут рискання [рад] (-pi..+pi)
    float rollspeed;       // Кутова швидкість крену [рад/с]
    float pitchspeed;      // Кутова швидкість тангажу [рад/с]
    float yawspeed;        // Кутова швидкість рискання [рад/с]
} mavlink_attitude_payload_t;

// Функція акумуляції полінома CRC-16
static inline void crc_accumulate(uint8_t data, uint16_t *crcAccum) {
    uint8_t tmp = data ^ (uint8_t)(*crcAccum & 0xFF);
    tmp ^= (tmp << 4);
    *crcAccum = (*crcAccum >> 8) ^ ((uint16_t)tmp << 8) ^ ((uint16_t)tmp << 3) ^ ((uint16_t)tmp >> 4);
}

// Пакування повідомлення ATTITUDE у кадр MAVLink v2
uint16_t mavlink_pack_attitude(
    uint8_t sysid,
    uint8_t compid,
    uint8_t seq,
    const mavlink_attitude_payload_t *payload,
    uint8_t *tx_buf
) {
    uint8_t payload_len = sizeof(mavlink_attitude_payload_t); // 28 байтів

    // 1. Формування заголовка v2
    tx_buf[0] = MAVLINK_STX_V2;
    tx_buf[1] = payload_len;
    tx_buf[2] = 0x00; // Incompat flags
    tx_buf[3] = 0x00; // Compat flags
    tx_buf[4] = seq;
    tx_buf[5] = sysid;
    tx_buf[6] = compid;
    tx_buf[7] = (uint8_t)(MAVLINK_MSG_ID_ATTITUDE & 0xFF);
    tx_buf[8] = (uint8_t)((MAVLINK_MSG_ID_ATTITUDE >> 8) & 0xFF);
    tx_buf[9] = (uint8_t)((MAVLINK_MSG_ID_ATTITUDE >> 16) & 0xFF);

    // 2. Копіювання корисних даних
    memcpy(&tx_buf[10], payload, payload_len);

    // 3. Розрахунок контрольної суми CRC над заголовком і даними
    uint16_t checksum = 0xFFFF;
    for (uint16_t i = 1; i < (10 + payload_len); ++i) {
        crc_accumulate(tx_buf[i], &checksum);
    }
    // Домішуємо байт CRC_EXTRA схеми
    crc_accumulate(MAVLINK_CRC_EXTRA_ATTITUDE, &checksum);

    // 4. Запис контрольної суми (Little-Endian)
    tx_buf[10 + payload_len] = (uint8_t)(checksum & 0xFF);
    tx_buf[11 + payload_len] = (uint8_t)((checksum >> 8) & 0xFF);

    return 12 + payload_len; // Повний розмір кадру = 40 байтів
}

// Десеріалізація повідомлення ATTITUDE
bool mavlink_unpack_attitude(
    const uint8_t *payload_buf,
    uint8_t payload_len,
    mavlink_attitude_payload_t *out_payload
) {
    if (payload_len < sizeof(mavlink_attitude_payload_t)) {
        // Якщо застосовано Zero-Truncation, очищаємо нулями і копіюємо отримане
        memset(out_payload, 0, sizeof(mavlink_attitude_payload_t));
        memcpy(out_payload, payload_buf, payload_len);
        return true;
    }
    memcpy(out_payload, payload_buf, sizeof(mavlink_attitude_payload_t));
    return true;
}

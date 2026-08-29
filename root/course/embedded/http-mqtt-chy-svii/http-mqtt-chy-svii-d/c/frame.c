/* frame.c — збирання й розбирання бінарного кадру.
 *
 * Уся робота йде в буфері, який дав викликач: жодного malloc, жодного
 * snprintf. На Cortex-M0 цей файл важить близько двох кілобайтів Flash. */
#include "frame.h"

#include <string.h>

/* CRC-16-CCITT (поліном 0x1021, початкове значення 0xFFFF).
 * Побітовий варіант: 8 ітерацій на байт, зате нуль байтів таблиці в RAM.
 * Де є вільні 512 байтів Flash — ставлять табличний, він у ~8 разів швидший. */
uint16_t frame_crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int bit = 0; bit < 8; bit++) {
            if (crc & 0x8000u) {
                crc = (uint16_t)((crc << 1) ^ 0x1021u);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

int frame_pack_telemetry(const sensor_sample_t *sample, uint16_t seq,
                         uint8_t *buf, size_t cap)
{
    if (sample == NULL || buf == NULL) {
        return FRAME_E_SPACE;
    }
    if (cap < sizeof(sensor_packet_t)) {
        return FRAME_E_SPACE;
    }

    sensor_packet_t pkt;
    /* Нулюємо структуру цілком: інакше в ефір поїхало б сміття зі стека —
     * а на упакованій структурі без padding це просто неініціалізовані поля. */
    memset(&pkt, 0, sizeof pkt);

    pkt.magic       = FRAME_MAGIC;
    pkt.msg_type    = MSG_TELEMETRY;
    pkt.seq_num     = seq;
    pkt.timestamp   = sample->timestamp;
    pkt.temperature = sample->temperature;
    pkt.humidity    = sample->humidity;
    pkt.vbat_mv     = sample->vbat_mv;

    /* CRC рахуємо по всьому кадру, крім самого поля crc16 (останні 2 байти). */
    pkt.crc16 = frame_crc16((const uint8_t *)&pkt,
                            sizeof pkt - sizeof pkt.crc16);

    memcpy(buf, &pkt, sizeof pkt);
    return (int)sizeof pkt;
}

int frame_parse_telemetry(const uint8_t *buf, size_t len, sensor_packet_t *out)
{
    if (len < sizeof(sensor_packet_t)) {
        return FRAME_E_SHORT;
    }

    sensor_packet_t pkt;
    /* Копіюємо в свою структуру, а не читаємо через покажчик у буфер:
     * буфер прийому може лежати без потрібного вирівнювання. */
    memcpy(&pkt, buf, sizeof pkt);

    if (pkt.magic != FRAME_MAGIC) {
        return FRAME_E_MAGIC;
    }
    if (pkt.msg_type != MSG_TELEMETRY) {
        return FRAME_E_TYPE;
    }

    uint16_t want = frame_crc16(buf, sizeof pkt - sizeof pkt.crc16);
    if (want != pkt.crc16) {
        return FRAME_E_CRC;
    }

    if (out != NULL) {
        *out = pkt;
    }
    return FRAME_OK;
}

/* Підтвердження — чотири байти: магія, тип, номер кадру.
 * CRC тут зайвий: єдине поле, що несе сенс, — seq, і хибний seq просто
 * не збігається з очікуваним, тобто відкидається тією ж перевіркою. */
int frame_pack_ack(uint16_t seq, uint8_t *buf, size_t cap)
{
    if (buf == NULL || cap < ACK_SIZE) {
        return FRAME_E_SPACE;
    }
    buf[0] = (uint8_t)FRAME_MAGIC;
    buf[1] = (uint8_t)MSG_ACK;
    buf[2] = (uint8_t)(seq & 0xFFu);
    buf[3] = (uint8_t)(seq >> 8);
    return (int)ACK_SIZE;
}

int frame_parse_ack(const uint8_t *buf, size_t len, uint16_t *seq_out)
{
    if (len < ACK_SIZE) {
        return FRAME_E_SHORT;
    }
    if (buf[0] != FRAME_MAGIC) {
        return FRAME_E_MAGIC;
    }
    if (buf[1] != MSG_ACK) {
        return FRAME_E_TYPE;
    }
    if (seq_out != NULL) {
        *seq_out = (uint16_t)((uint16_t)buf[2] | ((uint16_t)buf[3] << 8));
    }
    return FRAME_OK;
}

const char *frame_strerror(int code)
{
    switch (code) {
    case FRAME_OK:      return "ok";
    case FRAME_E_SHORT: return "датаграма коротша за кадр";
    case FRAME_E_MAGIC: return "чужа магія";
    case FRAME_E_TYPE:  return "не той тип повідомлення";
    case FRAME_E_CRC:   return "не збігся CRC";
    case FRAME_E_SPACE: return "замалий буфер";
    default:            return "невідомий код";
    }
}

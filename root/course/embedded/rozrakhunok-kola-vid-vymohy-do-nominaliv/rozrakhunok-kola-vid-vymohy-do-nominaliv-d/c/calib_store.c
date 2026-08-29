#include "calib_store.h"

static const uint8_t CALIB_MAGIC[4] = { 'C', 'A', 'L', '1' };

/* CRC-16/CCITT-FALSE: поліном 0x1021, початкове значення 0xFFFF,
   без відображення бітів і без фінального XOR. Табличний варіант тут зайвий —
   14 байтів раз на завантаження не варті 512 байтів Flash під таблицю. */
uint16_t calib_crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;
    size_t i;
    int bit;

    if (data == NULL) {
        return 0u;
    }
    for (i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

static void put_u32(uint8_t *dst, uint32_t v)
{
    dst[0] = (uint8_t)(v & 0xFFu);
    dst[1] = (uint8_t)((v >> 8) & 0xFFu);
    dst[2] = (uint8_t)((v >> 16) & 0xFFu);
    dst[3] = (uint8_t)((v >> 24) & 0xFFu);
}

static uint32_t get_u32(const uint8_t *src)
{
    return (uint32_t)src[0]
         | ((uint32_t)src[1] << 8)
         | ((uint32_t)src[2] << 16)
         | ((uint32_t)src[3] << 24);
}

calib_status_t calib_pack(const divider_cal_t *cal, uint8_t *buf, size_t len)
{
    uint16_t crc;

    if (cal == NULL || buf == NULL || len < CALIB_BLOB_SIZE) {
        return CALIB_ERR_BUFFER;
    }
    if (divider_check_cal(cal) != DIV_OK) {
        return CALIB_ERR_VALUE;   /* сміття в EEPROM не кладемо навіть свідомо */
    }

    buf[0] = CALIB_MAGIC[0];
    buf[1] = CALIB_MAGIC[1];
    buf[2] = CALIB_MAGIC[2];
    buf[3] = CALIB_MAGIC[3];
    /* Знакове значення записуємо через його бітове подання: перетворення
       int32 -> uint32 у C визначене однозначно (за модулем 2^32). */
    put_u32(&buf[4], (uint32_t)cal->offset_mv);
    put_u32(&buf[8], cal->gain_ppm);

    crc = calib_crc16(buf, 12u);
    buf[12] = (uint8_t)(crc & 0xFFu);
    buf[13] = (uint8_t)((crc >> 8) & 0xFFu);
    return CALIB_OK;
}

calib_status_t calib_unpack(const uint8_t *buf, size_t len, divider_cal_t *out)
{
    divider_cal_t cal;
    uint16_t crc_stored;
    uint16_t crc_actual;

    if (buf == NULL || out == NULL || len < CALIB_BLOB_SIZE) {
        return CALIB_ERR_BUFFER;
    }
    if (buf[0] != CALIB_MAGIC[0] || buf[1] != CALIB_MAGIC[1]
        || buf[2] != CALIB_MAGIC[2] || buf[3] != CALIB_MAGIC[3]) {
        return CALIB_ERR_MAGIC;
    }

    crc_stored = (uint16_t)((uint16_t)buf[12] | ((uint16_t)buf[13] << 8));
    crc_actual = calib_crc16(buf, 12u);
    if (crc_stored != crc_actual) {
        return CALIB_ERR_CRC;
    }

    cal.offset_mv = (int32_t)get_u32(&buf[4]);
    cal.gain_ppm  = get_u32(&buf[8]);

    /* CRC ловить биті байти, але не ловить помилки самого калібрування:
       нахил 3.0 міг бути порахований і записаний цілком коректно. */
    if (divider_check_cal(&cal) != DIV_OK) {
        return CALIB_ERR_VALUE;
    }

    *out = cal;
    return CALIB_OK;
}

const char *calib_status_str(calib_status_t st)
{
    switch (st) {
    case CALIB_OK:          return "ok";
    case CALIB_ERR_BUFFER:  return "замалий буфер";
    case CALIB_ERR_MAGIC:   return "запису калібрування немає";
    case CALIB_ERR_CRC:     return "CRC не збігся";
    case CALIB_ERR_VALUE:   return "коефіцієнти поза смугою";
    default:                return "невідомий стан";
    }
}

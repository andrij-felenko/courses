/* ==========================================================================
 *  mag_cal_storage.c — CRC32, пакування запису й робота з Flash
 * ========================================================================== */

#include <math.h>
#include <string.h>

#include "mag_cal_linalg.h"
#include "mag_cal_storage.h"

const char *mag_cal_storage_status_str(mag_cal_storage_status_t st) {
    switch (st) {
        case MAG_CAL_STORAGE_OK:            return "ok";
        case MAG_CAL_STORAGE_IO_ERROR:      return "помилка доступу до Flash";
        case MAG_CAL_STORAGE_BAD_CRC:       return "CRC32 не збіглася";
        case MAG_CAL_STORAGE_BAD_VALUES:    return "нефізичні коефіцієнти";
        case MAG_CAL_STORAGE_POOR_FITNESS:  return "збережена нев'язка завелика";
        case MAG_CAL_STORAGE_VERIFY_FAILED: return "перевірка після запису не пройшла";
        default:                            return "невідомий стан";
    }
}

/* CRC-32/ISO-HDLC (той самий поліном, що в Ethernet і zip), відображений
 * вигляд 0xEDB88320. Рахуємо побітово: таблиця на 1 КБ у Flash контролера
 * дорожча за 60 байтів даних, які ми нею перевіряємо. */
uint32_t mag_cal_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint32_t)data[i];
        for (int bit = 0; bit < 8; bit++) {
            const uint32_t mask = (uint32_t)(-(int32_t)(crc & 1u));
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return crc ^ 0xFFFFFFFFu;
}

/* --- Байтові примітиви little-endian --- */

static void put_u32(uint8_t *dst, uint32_t v) {
    dst[0] = (uint8_t)(v & 0xFFu);
    dst[1] = (uint8_t)((v >> 8) & 0xFFu);
    dst[2] = (uint8_t)((v >> 16) & 0xFFu);
    dst[3] = (uint8_t)((v >> 24) & 0xFFu);
}

static uint32_t get_u32(const uint8_t *src) {
    return (uint32_t)src[0]
         | ((uint32_t)src[1] << 8)
         | ((uint32_t)src[2] << 16)
         | ((uint32_t)src[3] << 24);
}

static void put_f32(uint8_t *dst, float v) {
    uint32_t bits;
    memcpy(&bits, &v, sizeof(bits));   /* єдиний законний спосіб побачити біти */
    put_u32(dst, bits);
}

static float get_f32(const uint8_t *src) {
    const uint32_t bits = get_u32(src);
    float v;
    memcpy(&v, &bits, sizeof(v));
    return v;
}

void mag_cal_record_pack(mag_cal_result_t *cal, uint8_t buf[MAG_CAL_RECORD_SIZE]) {
    memset(buf, 0, MAG_CAL_RECORD_SIZE);

    put_f32(&buf[0], cal->offset.x);
    put_f32(&buf[4], cal->offset.y);
    put_f32(&buf[8], cal->offset.z);

    size_t pos = 12;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            put_f32(&buf[pos], cal->soft_iron.m[i][j]);
            pos += 4;
        }
    }

    put_f32(&buf[48], cal->earth_field);
    put_f32(&buf[52], cal->rms_residual);

    cal->crc32 = mag_cal_crc32(buf, MAG_CAL_RECORD_SIZE - 4u);
    put_u32(&buf[56], cal->crc32);
}

mag_cal_storage_status_t mag_cal_record_unpack(const uint8_t buf[MAG_CAL_RECORD_SIZE],
                                               mag_cal_result_t *out) {
    const uint32_t stored   = get_u32(&buf[56]);
    const uint32_t computed = mag_cal_crc32(buf, MAG_CAL_RECORD_SIZE - 4u);
    if (stored != computed) {
        return MAG_CAL_STORAGE_BAD_CRC;
    }

    memset(out, 0, sizeof(*out));
    out->offset.x = get_f32(&buf[0]);
    out->offset.y = get_f32(&buf[4]);
    out->offset.z = get_f32(&buf[8]);

    size_t pos = 12;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            out->soft_iron.m[i][j] = get_f32(&buf[pos]);
            pos += 4;
        }
    }

    out->earth_field  = get_f32(&buf[48]);
    out->rms_residual = get_f32(&buf[52]);
    out->crc32        = stored;

    /* Збіжна CRC доводить лише цілісність байтів. Сміття, записане цілим,
     * лишається сміттям — тому перевіряємо ще й фізичний зміст чисел. */
    if (!isfinite(out->offset.x) || !isfinite(out->offset.y) || !isfinite(out->offset.z) ||
        !isfinite(out->earth_field) || !isfinite(out->rms_residual)) {
        return MAG_CAL_STORAGE_BAD_VALUES;
    }
    if (fabsf(out->offset.x) > MAG_CAL_MAX_OFFSET_UT ||
        fabsf(out->offset.y) > MAG_CAL_MAX_OFFSET_UT ||
        fabsf(out->offset.z) > MAG_CAL_MAX_OFFSET_UT) {
        return MAG_CAL_STORAGE_BAD_VALUES;
    }
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (!isfinite(out->soft_iron.m[i][j]) ||
                fabsf(out->soft_iron.m[i][j]) > MAG_CAL_MAX_GAIN) {
                return MAG_CAL_STORAGE_BAD_VALUES;
            }
        }
    }
    if (out->earth_field < 10.0f || out->earth_field > 100.0f) {
        return MAG_CAL_STORAGE_BAD_VALUES;
    }

    out->condition_num = mat3_condition(&out->soft_iron);
    out->sphere_radius = out->earth_field;

    if (out->rms_residual > MAG_CAL_MAX_RMS_UT ||
        out->condition_num >= MAG_CAL_MAX_CONDITION) {
        return MAG_CAL_STORAGE_POOR_FITNESS;
    }

    out->is_valid = true;
    return MAG_CAL_STORAGE_OK;
}

mag_cal_storage_status_t mag_cal_storage_save(mag_cal_result_t *cal) {
    uint8_t buf[MAG_CAL_RECORD_SIZE];
    mag_cal_record_pack(cal, buf);

    if (!mag_cal_flash_erase()) {
        return MAG_CAL_STORAGE_IO_ERROR;
    }
    if (!mag_cal_flash_write(buf, MAG_CAL_RECORD_SIZE)) {
        return MAG_CAL_STORAGE_IO_ERROR;
    }

    /* Зчитуємо назад те саме місце: у Flash буває напівстертий сектор,
     * який приймає запис, але тримає біти лише до першого прогрівання. */
    uint8_t verify[MAG_CAL_RECORD_SIZE];
    if (!mag_cal_flash_read(verify, MAG_CAL_RECORD_SIZE)) {
        return MAG_CAL_STORAGE_IO_ERROR;
    }
    if (memcmp(buf, verify, MAG_CAL_RECORD_SIZE) != 0) {
        return MAG_CAL_STORAGE_VERIFY_FAILED;
    }
    return MAG_CAL_STORAGE_OK;
}

mag_cal_storage_status_t mag_cal_storage_load(mag_cal_result_t *out) {
    uint8_t buf[MAG_CAL_RECORD_SIZE];
    if (!mag_cal_flash_read(buf, MAG_CAL_RECORD_SIZE)) {
        *out = MAG_CAL_IDENTITY_RESULT;
        return MAG_CAL_STORAGE_IO_ERROR;
    }

    const mag_cal_storage_status_t st = mag_cal_record_unpack(buf, out);
    if (st != MAG_CAL_STORAGE_OK) {
        /* Некалібрований стан кращий за напівпрочитаний: контур керування
         * дістане сирі виміри, а не випадково перекручені. */
        *out = MAG_CAL_IDENTITY_RESULT;
    }
    return st;
}

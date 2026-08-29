/* ==========================================================================
 *  mag_cal_storage.h — серіалізація калібрування у 60 байтів і збереження
 *  в енергонезалежній пам'яті з контролем цілісності CRC32.
 *
 *      байти 00..11 — вектор Hard Iron V0        (3 × float)
 *      байти 12..47 — матриця Soft Iron W        (9 × float, по рядках)
 *      байти 48..51 — еталонний модуль поля      (float)
 *      байти 52..55 — залишкова нев'язка RMS     (float)
 *      байти 56..59 — контрольна сума CRC32      (uint32)
 *
 *  Формат явно байтовий і little-endian: структуру C не пишемо у Flash як
 *  є, бо доповнення полів і порядок байтів мовчки змінюються з компілятором.
 * ========================================================================== */
#ifndef MAG_CAL_STORAGE_H
#define MAG_CAL_STORAGE_H

#include <stddef.h>

#include "mag_cal_types.h"

#define MAG_CAL_RECORD_SIZE 60u

typedef enum {
    MAG_CAL_STORAGE_OK = 0,
    MAG_CAL_STORAGE_IO_ERROR,      /* Flash не прочитався або не записався */
    MAG_CAL_STORAGE_BAD_CRC,       /* контрольна сума не збіглася */
    MAG_CAL_STORAGE_BAD_VALUES,    /* NaN чи нефізичні коефіцієнти */
    MAG_CAL_STORAGE_POOR_FITNESS,  /* збережена нев'язка гірша за 3.0 мкТл */
    MAG_CAL_STORAGE_VERIFY_FAILED  /* зчитане після запису не збіглося */
} mag_cal_storage_status_t;

const char *mag_cal_storage_status_str(mag_cal_storage_status_t st);

uint32_t mag_cal_crc32(const uint8_t *data, size_t len);

/* Пакування та розбір буфера. Пакувальник заповнює поле crc32 у result. */
void mag_cal_record_pack(mag_cal_result_t *cal, uint8_t buf[MAG_CAL_RECORD_SIZE]);
mag_cal_storage_status_t mag_cal_record_unpack(const uint8_t buf[MAG_CAL_RECORD_SIZE],
                                               mag_cal_result_t *out);

/* Запис із обов'язковим зворотним читанням: сектор Flash міг не стертися,
 * і тихо зіпсоване калібрування гірше за відсутнє. */
mag_cal_storage_status_t mag_cal_storage_save(mag_cal_result_t *cal);
mag_cal_storage_status_t mag_cal_storage_load(mag_cal_result_t *out);

/* --- Порт плати. Реалізує BSP конкретного контролера: сектор Flash,
 *     сторінка EEPROM або файл у LittleFS — конвеєру байдуже. --- */
bool mag_cal_flash_erase(void);
bool mag_cal_flash_write(const uint8_t *data, size_t len);
bool mag_cal_flash_read(uint8_t *data, size_t len);

#endif /* MAG_CAL_STORAGE_H */

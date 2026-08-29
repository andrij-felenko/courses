#ifndef CALIB_STORE_H
#define CALIB_STORE_H

#include <stddef.h>
#include <stdint.h>

#include "divider.h"

/* Зберігання калібрувальних коефіцієнтів в енергонезалежній пам'яті.
   Модуль навмисно не знає, що це за пам'ять: він пакує запис у масив байтів,
   а хто його понесе в EEPROM, у сектор Flash чи в файл — справа виклику.

   Розкладка запису (14 байтів, порядок little-endian):
       [0..3]   магія "CAL1"
       [4..7]   offset_mv, int32
       [8..11]  gain_ppm,  uint32
       [12..13] CRC-16/CCITT-FALSE перших 12 байтів                        */

#define CALIB_BLOB_SIZE 14u

typedef enum {
    CALIB_OK = 0,
    CALIB_ERR_BUFFER,   /* замалий буфер або нульовий вказівник */
    CALIB_ERR_MAGIC,    /* сторінка чиста (0xFF) або зайнята чимось іншим */
    CALIB_ERR_CRC,      /* запис побився: обрив живлення під час запису, знос комірки */
    CALIB_ERR_VALUE     /* CRC збігся, але коефіцієнти безглузді */
} calib_status_t;

calib_status_t calib_pack(const divider_cal_t *cal, uint8_t *buf, size_t len);
calib_status_t calib_unpack(const uint8_t *buf, size_t len, divider_cal_t *out);

uint16_t calib_crc16(const uint8_t *data, size_t len);
const char *calib_status_str(calib_status_t st);

#endif /* CALIB_STORE_H */

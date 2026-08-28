#include <stdint.h>
#include <string.h>
#include <stdlib.h>   // realloc для масивів, що ростуть
#include <stdio.h>

#define HEAD_BYTE1  0xA3
#define HEAD_BYTE2  0x95
#define LOG_FORMAT_MSG  0x80   // тип запису FMT (креслення) — 128

// Креслення одного типу повідомлення, витягнуте з FMT-запису.
typedef struct {
    uint8_t  type;        // код типу, який це креслення описує
    uint8_t  length;      // повна довжина ТАКОГО запису в байтах (з шапкою)
    char     name[5];     // "ATT", "GPS", "BAT" (+ '\0')
    char     format[17];  // рядок типів полів: "Qffffff" (+ '\0')
    uint8_t  n_fields;    // скільки полів (= довжина format)
} MsgFormat;

static MsgFormat fmt_table[256];   // креслення за кодом типу; 0 length = ще не знаємо

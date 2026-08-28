// nmea_core.c — контрольна сума й переведення поля координати.
// Ці дві функції однакові на будь-якій платформі.
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// XOR усіх байтів між '$' і '*'. Повертає 1, якщо збіглося з полем після '*'.
// line — цілий рядок NMEA, що починається з '$' і містить "*hh".
int nmea_checksum_ok(const char *line) {
    const char *p = line;
    if (*p == '$') p++;                 // пропустити відкривне '$'
    uint8_t sum = 0;
    while (*p && *p != '*') {           // XOR до зірки (не включно)
        sum ^= (uint8_t)*p;
        p++;
    }
    if (*p != '*') return 0;            // немає зірки — рядок обрізаний
    // після '*' — дві шістнадцяткові цифри контрольної суми
    unsigned int given = (unsigned int)strtol(p + 1, NULL, 16);
    return (given == sum);
}

// Поле "ddmm.mmmm" + літера напрямку → десяткові градуси.
// deg_digits: 2 для широти (dd), 3 для довготи (ddd).
double nmea_to_degrees(const char *field, char dir, int deg_digits) {
    if (!field || field[0] == '\0') return 0.0;   // порожнє поле — нема fix
    double raw = atof(field);                      // напр. 4807.038
    int deg = (int)(raw / 100.0);                  // 48  (відкидаємо хвилини)
    double minutes = raw - deg * 100.0;            // 7.038
    double dec = deg + minutes / 60.0;             // 48.1173
    if (dir == 'S' || dir == 'W') dec = -dec;      // південь/захід — мінус
    return dec;
}

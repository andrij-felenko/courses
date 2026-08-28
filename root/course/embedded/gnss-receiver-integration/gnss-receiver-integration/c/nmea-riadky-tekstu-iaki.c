// Перевірка контрольної суми NMEA-рядка.
// s указує на перший символ ПІСЛЯ '$', і рядок містить '*HH' у кінці.
bool nmea_checksum_ok(const char *s) {
    uint8_t sum = 0;
    while (*s && *s != '*') {
        sum ^= (uint8_t)*s;   // XOR усіх байтів між '$' і '*'
        s++;
    }
    if (*s != '*') return false;          // '*' не знайдено — рядок обірвано
    uint8_t given = (uint8_t)strtol(s + 1, NULL, 16);  // дві hex-цифри після '*'
    return sum == given;
}

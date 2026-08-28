#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

#define SN_LENGTH 14

typedef struct {
    char prefix[3];       // "SN", "GW", "CT"
    uint8_t year;         // 26 -> 2026
    uint8_t week;         // 01..53
    uint16_t model_code;  // 001..999
    uint16_t sequence;    // 0001..9999
    uint8_t checksum;     // 0..9
} device_sn_t;

/* Обчислення контрольної цифри за алгоритмом Луна для цифрової частини */
static bool validate_luhn_digit(const char *digits, size_t len) {
    int sum = 0;
    bool alternate = false;

    for (int i = (int)len - 1; i >= 0; i--) {
        if (!isdigit((unsigned char)digits[i])) {
            return false;
        }
        int n = digits[i] - '0';
        if (alternate) {
            n *= 2;
            if (n > 9) {
                n = (n % 10) + 1;
            }
        }
        sum += n;
        alternate = !alternate;
    }
    return (sum % 10 == 0);
}

/* Розбір та перевірка цілісності серійного номера */
bool parse_and_validate_sn(const char *raw_sn, device_sn_t *out_sn) {
    if (!raw_sn || strlen(raw_sn) != SN_LENGTH || !out_sn) {
        return false;
    }

    // Перевірка префікса
    if (!isupper((unsigned char)raw_sn[0]) || !isupper((unsigned char)raw_sn[1])) {
        return false;
    }
    out_sn->prefix[0] = raw_sn[0];
    out_sn->prefix[1] = raw_sn[1];
    out_sn->prefix[2] = '\0';

    // Перевірка алгоритмом Луна цифрової частини (позиції 2..13)
    if (!validate_luhn_digit(raw_sn + 2, SN_LENGTH - 2)) {
        return false;
    }

    // Видобування числових полів
    out_sn->year = (uint8_t)((raw_sn[2] - '0') * 10 + (raw_sn[3] - '0'));
    out_sn->week = (uint8_t)((raw_sn[4] - '0') * 10 + (raw_sn[5] - '0'));
    out_sn->model_code = (uint16_t)((raw_sn[6] - '0') * 100 + 
                                    (raw_sn[7] - '0') * 10 + 
                                    (raw_sn[8] - '0'));
    out_sn->sequence = (uint16_t)((raw_sn[9] - '0') * 1000 + 
                                  (raw_sn[10] - '0') * 100 + 
                                  (raw_sn[11] - '0') * 10 + 
                                  (raw_sn[12] - '0'));
    out_sn->checksum = (uint8_t)(raw_sn[13] - '0');

    if (out_sn->week < 1 || out_sn->week > 53) {
        return false;
    }
    return true;
}

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Швидкий парсер рядка YYYY-MM-DDTHH:MM:SSZ у секунди від Unix Epoch */
bool parse_rfc3339_fast(const char *str, int64_t *out_epoch_sec) {
    if (strlen(str) < 20) return false;
    if (str[4] != '-' || str[7] != '-' || (str[10] != 'T' && str[10] != 't') ||
        str[13] != ':' || str[16] != ':') {
        return false;
    }

    int year = (str[0] - '0') * 1000 + (str[1] - '0') * 100 + 
               (str[2] - '0') * 10 + (str[3] - '0');
    int month = (str[5] - '0') * 10 + (str[6] - '0');
    int day = (str[8] - '0') * 10 + (str[9] - '0');
    int hour = (str[11] - '0') * 10 + (str[12] - '0');
    int min = (str[14] - '0') * 10 + (str[15] - '0');
    int sec = (str[17] - '0') * 10 + (str[18] - '0');

    if (month < 1 || month > 12 || day < 1 || day > 31 ||
        hour > 23 || min > 59 || sec > 60) {
        return false;
    }

    int y = year - (month <= 2 ? 1 : 0);
    int m = month <= 2 ? month + 9 : month - 3;
    int era = (y >= 0 ? y : y - 399) / 400;
    unsigned yoe = (unsigned)(y - era * 400);
    unsigned doy = (153 * (unsigned)m + 2) / 5 + (unsigned)day - 1;
    unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    int64_t days = (int64_t)era * 146097 + (int64_t)doe - 719468;

    *out_epoch_sec = days * 86400LL + hour * 3600LL + min * 60LL + sec;
    return true;
}

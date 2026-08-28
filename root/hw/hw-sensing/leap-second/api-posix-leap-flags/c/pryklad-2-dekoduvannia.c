#include <stdio.h>
#include <stdint.h>

typedef enum {
    NTP_LEAP_NONE      = 0,
    NTP_LEAP_ADD_SEC   = 1,
    NTP_LEAP_DEL_SEC   = 2,
    NTP_LEAP_NOT_SYNC  = 3
} ntp_leap_t;

ntp_leap_t parse_ntp_first_byte(uint8_t header_byte) {
    return (ntp_leap_t)((header_byte >> 6) & 0x03);
}

void describe_ntp_status(uint8_t header_byte) {
    ntp_leap_t leap = parse_ntp_first_byte(header_byte);
    switch (leap) {
        case NTP_LEAP_NONE:
            printf("NTP LI = 00: Звичайний режим (корекція відсутня)\n");
            break;
        case NTP_LEAP_ADD_SEC:
            printf("NTP LI = 01: Заплановано додавання +1 секунди (23:59:60)\n");
            break;
        case NTP_LEAP_DEL_SEC:
            printf("NTP LI = 10: Заплановано вилучення 1 секунди (59 секунд у хвилині)\n");
            break;
        case NTP_LEAP_NOT_SYNC:
            printf("NTP LI = 11: Сервер розсинхронізовано (дані недостовірні)\n");
            break;
    }
}

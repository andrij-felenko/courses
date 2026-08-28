#include <stdio.h>

int main(void) {
    /* Байти запиту: CON GET /sensors/temp, MID=0x1234, Token=0xAB */
    const uint8_t raw_req[] = {
        0x41, 0x01, 0x12, 0x34,                  /* Ver=1, Type=0(CON), TKL=1, Code=0.01 (GET), MID=0x1234 */
        0xAB,                                    /* Token */
        0xB7, 's', 'e', 'n', 's', 'o', 'r', 's', /* Option Uri-Path (11), len 7 */
        0x04, 't', 'e', 'm', 'p'                 /* Option Uri-Path (delta 0 -> 11), len 4 */
    };

    coap_packet_t pkt;
    if (!coap_parse(raw_req, sizeof(raw_req), &pkt)) {
        return 1;
    }

    /* Перевірка вилучених полів */
    if (pkt.code == 1 && pkt.option_count == 2) {
        /* Перший сегмент шляху */
        if (pkt.options[0].number == 11 && pkt.options[0].length == 7) {
            if (memcmp(pkt.options[0].value, "sensors", 7) == 0) {
                return 0; /* Тест пройдено успішно */
            }
        }
    }

    return 1;
}

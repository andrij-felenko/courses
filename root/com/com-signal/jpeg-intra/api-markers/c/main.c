#include <stdio.h>
#include <stdint.h>

// Пройти сегменти JPEG у буфері buf (n байтів) і надрукувати структуру файлу.
void walk_jpeg(const uint8_t *buf, long n) {
    long i = 0;
    while (i + 1 < n) {
        if (buf[i] != 0xFF) { i++; continue; }       // маркер починається на 0xFF
        uint8_t m = buf[i + 1];
        if (m == 0xFF) { i++; continue; }             // 0xFF-заповнювач — пропустити
        i += 2;                                        // проковтнули «FF xx»

        if (m == 0xD8) { puts("SOI"); continue; }                  // стандалон
        if (m == 0xD9) { puts("EOI"); break;    }                  // стандалон, кінець
        if (m >= 0xD0 && m <= 0xD7) { printf("RST%d\n", m - 0xD0); continue; }

        long len = (buf[i] << 8) | buf[i + 1];         // big-endian; рахує себе + дані
        printf("FF%02X  довжина=%ld  даних=%ld\n", m, len, len - 2);

        if (m == 0xDA) {                               // SOS: далі — стиснутий потік
            i += len;                                  // перескочити заголовок скану…
            while (i + 1 < n) {                        // …і сам потік до наступного маркера
                if (buf[i] == 0xFF && buf[i + 1] != 0x00 &&
                    !(buf[i + 1] >= 0xD0 && buf[i + 1] <= 0xD7))
                    break;                             // справжній маркер (не FF00, не RSTn)
                i++;
            }
            continue;
        }
        i += len;                                      // на наступний сегмент
    }
}

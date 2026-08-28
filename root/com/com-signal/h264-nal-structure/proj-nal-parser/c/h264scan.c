/* h264scan.c — розбирач потоку H.264 Annex B.
   Збірка: cc -O2 -std=c11 -o h264scan h264scan.c
   Запуск: ./h264scan stream.h264                                       */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct {
    uint8_t *buf;      /* увесь потік у пам'яті   */
    long     len;
    long     pos;      /* звідки шукати далі      */
} annexb_t;

typedef struct {
    uint8_t *data;     /* байти одиниці без стартового коду й хвостових нулів */
    long     len;
    long     off;      /* зсув у файлі — щоб було що надрукувати */
} nal_t;

/* Повертає 1, якщо в потоці знайшлася ще одна одиниця. */
static int annexb_next(annexb_t *it, nal_t *out)
{
    uint8_t *b = it->buf;
    long n = it->len, i = it->pos, zeros = 0, begin = -1;

    /* 1. Стати на початок вантажу: пропустити нулі й одиничку. */
    while (i < n) {
        uint8_t c = b[i++];
        if      (c == 0x00)               zeros++;
        else if (c == 0x01 && zeros >= 2) { begin = i; break; }
        else                              zeros = 0;
    }
    if (begin < 0) { it->pos = n; return 0; }   /* стартових кодів більше немає */

    /* 2. Знайти початок НАСТУПНОГО коду — і саме початок, разом із нулями. */
    long end;
    zeros = 0;
    for (;;) {
        if (i == n) { end = n - zeros; it->pos = n; break; }
        uint8_t c = b[i++];
        if (c == 0x00) { zeros++; continue; }
        if (c == 0x01 && zeros >= 2) { end = i - 1 - zeros; it->pos = end; break; }
        zeros = 0;
    }

    out->data = b + begin;
    out->len  = end - begin;
    out->off  = begin;
    return 1;
}

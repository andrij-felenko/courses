#include <stdint.h>
#include <arpa/inet.h>

/* Базовий спільний заголовок RTCP */
typedef struct {
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    uint8_t  rc:5;        /* Report count */
    uint8_t  p:1;         /* Padding flag */
    uint8_t  version:2;   /* Protocol version (2) */
#elif __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    uint8_t  version:2;
    uint8_t  p:1;
    uint8_t  rc:5;
#endif
    uint8_t  pt;          /* Packet type (200=SR, 201=RR, 202=SDES) */
    uint16_t length;      /* Довжина в 32-бітних словах мінус 1 */
    uint32_t ssrc;        /* SSRC відправника цього звіту */
} __attribute__((packed)) RtcpHeader;

/* Блок звіту про якість одного джерела (Report Block) */
typedef struct {
    uint32_t ssrc;              /* SSRC джерела, про яке звітуємо */
    uint8_t  fraction_lost;     /* Втрати: число/256 */
    uint8_t  cumulative_lost[3];/* Знакове 24-бітне число втрат */
    uint32_t highest_seq_ext;   /* Старші 16 біт - цикли, молодші - seq */
    uint32_t jitter;            /* Джитер у квантах кодека */
    uint32_t lsr;               /* Middle 32-bits of NTP from last SR */
    uint32_t dlsr;              /* Затримка з моменту отримання SR */
} __attribute__((packed)) RtcpReportBlock;

/* Функція вилучення 24-бітного знакового лічильника втрат */
static inline int32_t unpack_cumulative_lost(const uint8_t bytes[3]) {
    int32_t val = (bytes[0] << 16) | (bytes[1] << 8) | bytes[2];
    /* Розширення знакового біта для 24-бітного додаткового коду */
    if (val & 0x00800000) {
        val |= 0xFF000000;
    }
    return val;
}

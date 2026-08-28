#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#pragma pack(push, 1)

/* 64-бітний формат мітки часу NTP (RFC 5905) */
typedef struct {
    uint32_t seconds;   /* Секунди від 1900-01-01 00:00:00 UTC (Big-Endian) */
    uint32_t fraction;  /* Дробова частина секунди (крок 232.83 пс) */
} ntp_timestamp_t;

/* Повний 48-байтний заголовок пакета NTPv4 */
typedef struct {
    uint8_t  li_vn_mode;       /* LI (2 біти), VN (3 біти), Mode (3 біти) */
    uint8_t  stratum;          /* Шар ієрархії (0..16) */
    int8_t   poll;             /* log2 інтервалу опитування */
    int8_t   precision;        /* log2 точності локального годинника */
    
    uint32_t root_delay;       /* s16.16 кругова затримка до первинного еталона */
    uint32_t root_dispersion;  /* u16.16 сумарна дисперсія еталона */
    uint32_t ref_id;           /* ASCII еталона або IPv4/MD5 адреса */
    
    ntp_timestamp_t ref_time;     /* Час останнього оновлення годинника */
    ntp_timestamp_t origin_time;  /* T1: відправка клієнтом */
    ntp_timestamp_t rx_time;      /* T2: прийом сервером */
    ntp_timestamp_t tx_time;      /* T3: відправка відповіді сервером */
} ntp_packet_t;

#pragma pack(pop)

/* Допоміжні функції для роботи з бітовими полями першого байта */
static inline uint8_t ntp_get_li(const ntp_packet_t *pkt) {
    return (pkt->li_vn_mode >> 6) & 0x03;
}

static inline uint8_t ntp_get_vn(const ntp_packet_t *pkt) {
    return (pkt->li_vn_mode >> 3) & 0x07;
}

static inline uint8_t ntp_get_mode(const ntp_packet_t *pkt) {
    return pkt->li_vn_mode & 0x07;
}

static inline void ntp_set_header(ntp_packet_t *pkt, uint8_t li, uint8_t vn, uint8_t mode) {
    pkt->li_vn_mode = (uint8_t)(((li & 0x03) << 6) | ((vn & 0x07) << 3) | (mode & 0x07));
}

/* Перевірка на отримання пакета Kiss-o'-Death */
static inline bool ntp_is_kod(const ntp_packet_t *pkt, char out_kod[5]) {
    if (pkt->stratum == 0) {
        memcpy(out_kod, &pkt->ref_id, 4);
        out_kod[4] = '\0';
        return true;
    }
    return false;
}

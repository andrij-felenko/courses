#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>
#include <math.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define NTP_PORT 123
#define NTP_UNIX_OFFSET 2208988800ULL
#define NTP_FRAC_SCALE 4294967296.0

#define NTP_STEP_THRESHOLD 0.128   /* 128 мс: поріг перемикання між slew та step */
#define NTP_PANIC_THRESHOLD 1000.0 /* 1000 с: поріг аварійної панічної зупинки */

#pragma pack(push, 1)

/* 48-байтний заголовок пакета SNTPv4 (RFC 4330) */
typedef struct {
    uint8_t  li_vn_mode;       /* LI (2 біти), VN (3 біти), Mode (3 біти) */
    uint8_t  stratum;          /* Шар еталона (0..16) */
    int8_t   poll;             /* log2 інтервалу опитування */
    int8_t   precision;        /* log2 точності генератора */
    uint32_t root_delay;       /* s16.16 затримка до первинного еталона */
    uint32_t root_dispersion;  /* u16.16 сумарна дисперсія еталона */
    uint32_t ref_id;           /* 4 ASCII або IPv4 адреса джерела */
    uint32_t ref_ts_sec;       /* Час останнього оновлення (секунди) */
    uint32_t ref_ts_frac;      /* Час останнього оновлення (дріб) */
    uint32_t orig_ts_sec;      /* T1: час відправки клієнтом (секунди) */
    uint32_t orig_ts_frac;     /* T1: час відправки клієнтом (дріб) */
    uint32_t rx_ts_sec;        /* T2: час прийому сервером (секунди) */
    uint32_t rx_ts_frac;       /* T2: час прийому сервером (дріб) */
    uint32_t tx_ts_sec;        /* T3: час відправки сервером (секунди) */
    uint32_t tx_ts_frac;       /* T3: час відправки сервером (дріб) */
} sntp_packet_t;

#pragma pack(pop)

/* Конвертація struct timespec у секунди формату double */
static inline double timespec_to_seconds(const struct timespec *ts) {
    return (double)ts->tv_sec + ((double)ts->tv_nsec / 1e9);
}

/* Конвертація 64-бітного NTP Timestamp у секунди епохи Unix */
static inline double ntp_to_unix_seconds(uint32_t sec_be, uint32_t frac_be) {
    uint32_t s = ntohl(sec_be);
    uint32_t f = ntohl(frac_be);
    if (s == 0 && f == 0) return 0.0;
    return ((double)(s - NTP_UNIX_OFFSET)) + ((double)f / NTP_FRAC_SCALE);
}

/* Конвертація секунд епохи Unix у 64-бітний NTP Timestamp */
static inline void unix_seconds_to_ntp(double unix_sec, uint32_t *out_sec_be, uint32_t *out_frac_be) {
    double int_part;
    double frac_part = modf(unix_sec, &int_part);
    *out_sec_be = htonl((uint32_t)(int_part + NTP_UNIX_OFFSET));
    *out_frac_be = htonl((uint32_t)(frac_part * NTP_FRAC_SCALE));
}

/* Дисципліна системного годинника ядра: Slew проти Step */
static int apply_clock_discipline(double offset) {
    double abs_offset = fabs(offset);

    if (abs_offset >= NTP_PANIC_THRESHOLD) {
        fprintf(stderr, "Критична помилка: зміщення %.3f с перевищує ліміт паніки (1000 с)!\n", offset);
        return -1;
    }

    if (abs_offset < NTP_STEP_THRESHOLD) {
        /* Плавне регулювання частоти кварцового генератора (Clock Slew) */
        struct timeval adj;
        adj.tv_sec = (time_t)offset;
        adj.tv_usec = (suseconds_t)((offset - (double)adj.tv_sec) * 1e6);
        
        if (adjtime(&adj, NULL) != 0) {
            perror("Помилка системного виклику adjtime");
            return -1;
        }
        printf("Дисципліна: виконано плавне коригування (slew) на %.6f с (монотонно)\n", offset);
    } else {
        /* Разовий стрибок системного часу (Clock Step) */
        struct timespec now;
        if (clock_gettime(CLOCK_REALTIME, &now) != 0) {
            perror("Помилка clock_gettime");
            return -1;
        }
        double target_sec = timespec_to_seconds(&now) + offset;
        struct timespec target;
        target.tv_sec = (time_t)target_sec;
        target.tv_nsec = (long)((target_sec - (double)target.tv_sec) * 1e9);

        if (clock_settime(CLOCK_REALTIME, &target) != 0) {
            perror("Помилка clock_settime (потрібні привілеї суперкористувача root)");
            return -1;
        }
        printf("Дисципліна: виконано разовий стрибок часу (step) на %.6f с\n", offset);
    }
    return 0;
}

/* Виконання мережевого запиту до сервера SNTP */
int query_sntp_server(const char *hostname, double *out_offset, double *out_delay) {
    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;

    char port_str[6];
    snprintf(port_str, sizeof(port_str), "%d", NTP_PORT);

    int rc = getaddrinfo(hostname, port_str, &hints, &res);
    if (rc != 0) {
        fprintf(stderr, "Помилка резолвінгу хоста %s: %s\n", hostname, gai_strerror(rc));
        return -1;
    }

    int fd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (fd < 0) {
        perror("Помилка створення сокета UDP");
        freeaddrinfo(res);
        return -1;
    }

    /* Налаштування тайм-ауту 3 секунди на очікування відповіді */
    struct timeval tv = {.tv_sec = 3, .tv_usec = 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    sntp_packet_t req;
    memset(&req, 0, sizeof(req));
    /* Формування першого байта: LI=0 (no warning), VN=4 (NTPv4), Mode=3 (Client) */
    req.li_vn_mode = (0 << 6) | (4 << 3) | 3;

    /* Фіксація локального часу відправки клієнта T1 */
    struct timespec ts_t1;
    clock_gettime(CLOCK_REALTIME, &ts_t1);
    double t1 = timespec_to_seconds(&ts_t1);
    unix_seconds_to_ntp(t1, &req.tx_ts_sec, &req.tx_ts_frac);

    if (sendto(fd, &req, sizeof(req), 0, res->ai_addr, res->ai_addrlen) < 0) {
        perror("Помилка відправки запиту sendto");
        close(fd);
        freeaddrinfo(res);
        return -1;
    }

    sntp_packet_t resp;
    struct sockaddr_storage from_addr;
    socklen_t from_len = sizeof(from_addr);

    ssize_t n = recvfrom(fd, &resp, sizeof(resp), 0, (struct sockaddr *)&from_addr, &from_len);
    
    /* Фіксація локального часу прийому клієнта T4 */
    struct timespec ts_t4;
    clock_gettime(CLOCK_REALTIME, &ts_t4);
    double t4 = timespec_to_seconds(&ts_t4);

    close(fd);
    freeaddrinfo(res);

    if (n < (ssize_t)sizeof(sntp_packet_t)) {
        fprintf(stderr, "Помилка прийому: отримано %zd байтів замість очікуваних 48\n", n);
        return -1;
    }

    /* Валідація полів заголовка */
    uint8_t li = (resp.li_vn_mode >> 6) & 0x03;
    uint8_t mode = resp.li_vn_mode & 0x07;
    uint8_t stratum = resp.stratum;

    if (mode != 4 && mode != 5) {
        fprintf(stderr, "Помилка: некоректний режим відповіді Mode=%d (очікувався Server=4)\n", mode);
        return -1;
    }

    /* Перевірка коду відмови Kiss-o'-Death */
    if (stratum == 0) {
        char kod[5] = {0};
        memcpy(kod, &resp.ref_id, 4);
        fprintf(stderr, "Сервер надіслав код відмови Kiss-o'-Death (Stratum 0): [%s]\n", kod);
        return -2;
    }

    /* Перевірка на розсинхронізований стан сервера */
    if (li == 3 || stratum >= 16) {
        fprintf(stderr, "Помилка: сервер розсинхронізований (LI=%d, Stratum=%d)\n", li, stratum);
        return -1;
    }

    /* Перевірка захисту від атак повторення: Origin Timestamp мусить дорівнювати T1 */
    if (resp.orig_ts_sec != req.tx_ts_sec || resp.orig_ts_frac != req.tx_ts_frac) {
        fprintf(stderr, "Помилка безпеки: Origin Timestamp не збігається з міткою запиту T1!\n");
        return -1;
    }

    double t2 = ntp_to_unix_seconds(resp.rx_ts_sec, resp.rx_ts_frac);
    double t3 = ntp_to_unix_seconds(resp.tx_ts_sec, resp.tx_ts_frac);

    /* Розрахунок затримки та зміщення за стандартом RFC 5905 */
    double delay = (t4 - t1) - (t3 - t2);
    double offset = ((t2 - t1) + (t3 - t4)) / 2.0;

    if (delay < 0.0) {
        fprintf(stderr, "Попередження: кругова затримка від'ємна (%.6f с), відкидаємо вибірку\n", delay);
        return -1;
    }

    *out_offset = offset;
    *out_delay = delay;

    printf("Успішний обмін: Stratum=%d, T1=%.6f, T2=%.6f, T3=%.6f, T4=%.6f\n", stratum, t1, t2, t3, t4);
    printf("Метрики зв'язку: Round-Trip Delay = %.6f с, Clock Offset = %.6f с\n", delay, offset);

    return 0;
}

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <sys/stat.h>

#define WAL_MAGIC 0x57414C31 /* Сигнатура "WAL1" */
#define SECTOR_SIZE 4096

/* Заголовок запису WAL */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint64_t lsn;
    uint32_t length;
    uint32_t crc32;
} wal_header_t;
#pragma pack(pop)

/* Таблична реалізація IEEE 802.3 CRC32 */
static uint32_t crc32_ieee(const void *data, size_t len) {
    static uint32_t table[256];
    static int have_table = 0;
    if (!have_table) {
        for (uint32_t i = 0; i < 256; i++) {
            uint32_t rem = i;
            for (int j = 0; j < 8; j++) {
                if (rem & 1) rem = (rem >> 1) ^ 0xEDB88320;
                else rem >>= 1;
            }
            table[i] = rem;
        }
        have_table = 1;
    }
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
        crc = table[(crc ^ p[i]) & 0xFF] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFF;
}

/* Отримання монотонного часу в мікросекундах */
static uint64_t current_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

typedef enum {
    SYNC_NONE,       /* Звичайний write() без синхронізації */
    SYNC_FDATASYNC,  /* write() + fdatasync() після кожного запису */
    SYNC_DIRECT_IO   /* O_DIRECT + O_DSYNC (вирівняні 4KB блоки) */
} sync_mode_t;

/* Запис транзакцій у файл журналу з вимірюванням затримок */
static int benchmark_wal_write(const char *filename, sync_mode_t mode, int total_tx) {
    int flags = O_CREAT | O_RDWR | O_TRUNC;
    if (mode == SYNC_DIRECT_IO) {
        flags |= O_DIRECT | O_DSYNC;
    }

    int fd = open(filename, flags, 0644);
    if (fd < 0) {
        perror("Помилка створення файлу WAL");
        return -1;
    }

    /* Виділення вирівняної пам'яті для O_DIRECT */
    void *raw_buf = NULL;
    if (posix_memalign(&raw_buf, SECTOR_SIZE, SECTOR_SIZE) != 0) {
        perror("Помилка posix_memalign");
        close(fd);
        return -1;
    }
    uint8_t *buffer = (uint8_t *)raw_buf;

    uint64_t start_total = current_time_us();
    uint64_t total_latency_us = 0;

    for (int i = 1; i <= total_tx; i++) {
        memset(buffer, 0, SECTOR_SIZE);
        wal_header_t *hdr = (wal_header_t *)buffer;
        hdr->magic = WAL_MAGIC;
        hdr->lsn = (uint64_t)i;

        char payload[128];
        snprintf(payload, sizeof(payload), "TX=%08d;FROM=ACC_%04d;TO=ACC_%04d;AMOUNT=%d.00;STATUS=COMMITTED",
                 i, rand() % 500, rand() % 500, (rand() % 1000) + 1);
        hdr->length = (uint32_t)strlen(payload);
        memcpy(buffer + sizeof(wal_header_t), payload, hdr->length);

        /* Контрольна сума для навантаження */
        hdr->crc32 = crc32_ieee(buffer + sizeof(wal_header_t), hdr->length);

        uint64_t tx_start = current_time_us();

        if (mode == SYNC_DIRECT_IO) {
            if (write(fd, buffer, SECTOR_SIZE) != SECTOR_SIZE) {
                perror("Помилка запису O_DIRECT");
                free(raw_buf);
                close(fd);
                return -1;
            }
        } else {
            size_t record_len = sizeof(wal_header_t) + hdr->length;
            if (write(fd, buffer, record_len) != (ssize_t)record_len) {
                perror("Помилка виклику write");
                free(raw_buf);
                close(fd);
                return -1;
            }
            if (mode == SYNC_FDATASYNC) {
                if (fdatasync(fd) < 0) {
                    perror("Помилка виклику fdatasync");
                    free(raw_buf);
                    close(fd);
                    return -1;
                }
            }
        }

        uint64_t tx_end = current_time_us();
        total_latency_us += (tx_end - tx_start);
    }

    uint64_t end_total = current_time_us();
    double elapsed_sec = (double)(end_total - start_total) / 1000000.0;
    double avg_lat_us = (double)total_latency_us / (double)total_tx;
    double tps = (double)total_tx / elapsed_sec;

    printf("  Транзакцій: %d | Загальний час: %.3f с | Середня затримка: %.1f мкс | Продуктивність: %.1f TPS\n",
           total_tx, elapsed_sec, avg_lat_us, tps);

    free(raw_buf);
    close(fd);
    return 0;
}

/* Сканування та валідація цілісності журналу після аварії */
static int recover_wal(const char *filename) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файлу для відновлення");
        return -1;
    }

    uint64_t valid_tx_count = 0;
    uint8_t buffer[SECTOR_SIZE];

    printf("--- Сканування журналу WAL: %s ---\n", filename);

    while (1) {
        wal_header_t hdr;
        ssize_t r = read(fd, &hdr, sizeof(wal_header_t));
        if (r == 0) break; /* Досягнуто кінця логу */
        if (r < (ssize_t)sizeof(wal_header_t)) {
            printf("  [УВАГА] Неповний заголовок наприкінці. Обірваний запис.\n");
            break;
        }

        if (hdr.magic != WAL_MAGIC) {
            printf("  [ПОМИЛКА] Невідповідність Magic: 0x%08X (пошкодження або кінець виділеного блоку)\n", hdr.magic);
            break;
        }

        if (hdr.length > sizeof(buffer)) {
            printf("  [ПОМИЛКА] Неприпустима довжина навантаження: %u байтів\n", hdr.length);
            break;
        }

        r = read(fd, buffer, hdr.length);
        if (r < (ssize_t)hdr.length) {
            printf("  [УВАГА] Неповне навантаження для LSN %llu. Зупинка відновлення.\n", (unsigned long long)hdr.lsn);
            break;
        }

        uint32_t calc_crc = crc32_ieee(buffer, hdr.length);
        if (calc_crc != hdr.crc32) {
            printf("  [ПОМИЛКА] Збій CRC32 для LSN %llu: розраховано 0x%08X, у заголовку 0x%08X\n",
                   (unsigned long long)hdr.lsn, calc_crc, hdr.crc32);
            break;
        }

        valid_tx_count++;
    }

    printf("--- Відновлення завершено. Валідних транзакцій: %llu ---\n\n", (unsigned long long)valid_tx_count);
    close(fd);
    return 0;
}

int main(void) {
    const int NUM_TX = 500;
    printf("=== БЕНЧМАРК ТА ВІДНОВЛЕННЯ ДОВГОВІЧНОСТІ ЖУРНАЛУ WAL ===\n\n");

    printf("1. Режим без синхронізації (Buffered write): виключно кеш сторінок:\n");
    benchmark_wal_write("test_wal_nosync.log", SYNC_NONE, NUM_TX);
    recover_wal("test_wal_nosync.log");

    printf("2. Режим буферизованого запису з fdatasync(): повна довговічність VFS:\n");
    benchmark_wal_write("test_wal_fdatasync.log", SYNC_FDATASYNC, NUM_TX);
    recover_wal("test_wal_fdatasync.log");

    printf("3. Режим прямого вводу-виводу (O_DIRECT | O_DSYNC): апаратний DMA:\n");
    benchmark_wal_write("test_wal_direct.log", SYNC_DIRECT_IO, NUM_TX);
    recover_wal("test_wal_direct.log");

    unlink("test_wal_nosync.log");
    unlink("test_wal_fdatasync.log");
    unlink("test_wal_direct.log");

    return 0;
}

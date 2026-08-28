#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <syslog.h>
#include <fcntl.h>
#include <string.h>

#define SWIOTLB_HIGHWATER "/sys/kernel/debug/swiotlb/io_tlb_used_highwater"
#define SWIOTLB_NSLABS    "/sys/kernel/debug/swiotlb/io_tlb_nslabs"
#define SWIOTLB_OVERFLOW  "/sys/kernel/debug/swiotlb/io_tlb_overflow"

static unsigned long read_val(const char *path) {
    char buf[64];
    int fd = open(path, O_RDONLY);
    if (fd < 0) return 0;
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return 0;
    buf[n] = '\0';
    return strtoul(buf, NULL, 10);
}

int main(void) {
    openlog("swiotlb-watcher", LOG_PID | LOG_CONS, LOG_DAEMON);
    syslog(LOG_INFO, "Запуск демона спостереження за пулом SWIOTLB");

    unsigned long nslabs = read_val(SWIOTLB_NSLABS);
    if (nslabs == 0) {
        syslog(LOG_ERR, "Не вдалося отримати розмір пулу SWIOTLB. Завершення роботи.");
        closelog();
        return EXIT_FAILURE;
    }

    unsigned long last_highwater = 0;
    unsigned long last_overflow = 0;

    while (1) {
        unsigned long cur_highwater = read_val(SWIOTLB_HIGHWATER);
        unsigned long cur_overflow = read_val(SWIOTLB_OVERFLOW);

        if (cur_overflow > last_overflow) {
            syslog(LOG_CRIT, "КРИТИЧНО: Зафіксовано нові переповнення пулу SWIOTLB (+%lu)! Загалом: %lu",
                   cur_overflow - last_overflow, cur_overflow);
            last_overflow = cur_overflow;
        }

        if (cur_highwater > last_highwater) {
            double pct = ((double)cur_highwater / (double)nslabs) * 100.0;
            if (pct > 75.0) {
                syslog(LOG_WARNING, "Попередження: Новий пік утилізації SWIOTLB: %lu слотів (%.1f%% від %lu)",
                       cur_highwater, pct, nslabs);
            }
            last_highwater = cur_highwater;
        }

        sleep(5);
    }

    closelog();
    return EXIT_SUCCESS;
}

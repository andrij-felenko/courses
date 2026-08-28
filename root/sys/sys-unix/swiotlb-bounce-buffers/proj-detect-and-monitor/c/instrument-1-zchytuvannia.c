#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define SWIOTLB_BASE "/sys/kernel/debug/swiotlb"
#define BUF_SIZE 64

static int read_debugfs_ulong(const char *node, unsigned long *val) {
    char path[256];
    char buf[BUF_SIZE];
    snprintf(path, sizeof(path), "%s/%s", SWIOTLB_BASE, node);

    int fd = open(path, O_RDONLY);
    if (fd < 0)
        return -errno;

    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (n <= 0)
        return -EIO;

    buf[n] = '\0';
    char *endptr;
    *val = strtoul(buf, &endptr, 10);
    return 0;
}

int main(void) {
    unsigned long nslabs = 0;
    unsigned long used = 0;
    unsigned long highwater = 0;
    unsigned long overflow = 0;

    if (read_debugfs_ulong("io_tlb_nslabs", &nslabs) < 0) {
        fprintf(stderr, "Помилка доступу до debugfs. Перевірте: mount -t debugfs none /sys/kernel/debug\n");
        return EXIT_FAILURE;
    }

    read_debugfs_ulong("io_tlb_used", &used);
    read_debugfs_ulong("io_tlb_used_highwater", &highwater);
    read_debugfs_ulong("io_tlb_overflow", &overflow);

    double total_mb = (double)(nslabs * 2048) / (1024.0 * 1024.0);
    double used_mb = (double)(used * 2048) / (1024.0 * 1024.0);
    double high_mb = (double)(highwater * 2048) / (1024.0 * 1024.0);
    double used_pct = nslabs ? ((double)used / (double)nslabs) * 100.0 : 0.0;
    double high_pct = nslabs ? ((double)highwater / (double)nslabs) * 100.0 : 0.0;

    printf("=== Стан підсистеми SWIOTLB ===\n");
    printf("Загальний пул:      %8lu слотів (%6.2f МіБ)\n", nslabs, total_mb);
    printf("Поточне утримання:  %8lu слотів (%6.2f МіБ) [%5.1f%%]\n", used, used_mb, used_pct);
    printf("Пікове утримання:   %8lu слотів (%6.2f МіБ) [%5.1f%%]\n", highwater, high_mb, high_pct);
    printf("Лічильник відмов:   %8lu переповнень\n", overflow);

    if (overflow > 0) {
        printf("\n[УВАГА] Зафіксовано переповнення пулу! Збільште параметр ядра swiotlb=N\n");
    } else if (high_pct > 80.0) {
        printf("\n[ПОПЕРЕДЖЕННЯ] Пікове навантаження перевищує 80%% ємності пулу.\n");
    } else {
        printf("\n[OK] Пул працює в штатному режимі із запасом пам'яті.\n");
    }

    return EXIT_SUCCESS;
}

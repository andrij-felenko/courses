/* pcr_reader.c — Програма зчитування банків PCR мовою C (POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define SYSFS_PCR_SHA256_FMT "/sys/class/tpm/tpm0/pcr-sha256/%u"
#define PCR_HEX_STRING_LEN 64

int read_pcr_sha256(unsigned int pcr_index, char *out_hex, size_t max_len) {
    if (pcr_index > 23 || max_len < PCR_HEX_STRING_LEN + 1) {
        errno = EINVAL;
        return -1;
    }

    char path[256];
    snprintf(path, sizeof(path), SYSFS_PCR_SHA256_FMT, pcr_index);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    ssize_t bytes_read = read(fd, out_hex, max_len - 1);
    close(fd);

    if (bytes_read <= 0) {
        return -1;
    }

    /* Видалення символу нового рядка, якщо він присутній */
    out_hex[bytes_read] = '\0';
    char *newline = strchr(out_hex, '\n');
    if (newline) {
        *newline = '\0';
    }

    return 0;
}

int main(void) {
    printf("--- Зчитання банків PCR-SHA256 через sysfs (C) ---\n");

    for (unsigned int i = 0; i <= 7; ++i) {
        char pcr_hex[128] = {0};
        if (read_pcr_sha256(i, pcr_hex, sizeof(pcr_hex)) == 0) {
            printf("PCR-%02u: %s\n", i, pcr_hex);
        } else {
            fprintf(stderr, "Помилка читання PCR-%02u: %s\n", i, strerror(errno));
        }
    }

    return EXIT_SUCCESS;
}

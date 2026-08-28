#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define PAGE_SIZE 4096

/*
 * Зчитує статус віртуальної сторінки з /proc/[pid]/pagemap.
 */
int inspect_pagemap_entry(pid_t pid, uintptr_t vaddr, uint64_t *entry) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/pagemap", pid);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    off_t offset = (off_t)((vaddr / PAGE_SIZE) * sizeof(uint64_t));
    if (lseek(fd, offset, SEEK_SET) == (off_t)-1) {
        close(fd);
        return -1;
    }

    ssize_t bytes_read = read(fd, entry, sizeof(uint64_t));
    close(fd);

    return (bytes_read == sizeof(uint64_t)) ? 0 : -1;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <pid> <hex_vaddr>\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    uintptr_t vaddr = (uintptr_t)strtoull(argv[2], NULL, 16);

    uint64_t entry = 0;
    if (inspect_pagemap_entry(pid, vaddr, &entry) != 0) {
        perror("inspect_pagemap_entry failed");
        return EXIT_FAILURE;
    }

    int present = (entry >> 63) & 1;
    int swapped = (entry >> 62) & 1;
    uint64_t pfn = entry & ((1ULL << 55) - 1);

    printf("=== Інспекція pagemap для PID=%d адреса=0x%lx ===\n", pid, vaddr);
    printf("Присутня у RAM (Present): %s\n", present ? "ТАК" : "НІ");
    printf("У свопі (Swapped):        %s\n", swapped ? "ТАК" : "НІ");
    if (present) {
        printf("Фізичний номер кадру PFN: 0x%lx (Фізична адреса: 0x%lx)\n", pfn, pfn * PAGE_SIZE);
    }

    return EXIT_SUCCESS;
}

#define _GNU_SOURCE
#include <link.h>
#include <stdio.h>
#include <stdint.h>

static int callback(struct dl_phdr_info *info, size_t size, void *data) {
    printf("Завантажений модуль: %s (базова адреса: 0x%lx)\n",
           info->dlpi_name[0] ? info->dlpi_name : "головний бінарник",
           info->dlpi_addr);
    for (int i = 0; i < info->dlpi_phnum; ++i) {
        if (info->dlpi_phdr[i].p_type == PT_NOTE) {
            const uint8_t *note_addr = (const uint8_t *)(info->dlpi_addr + info->dlpi_phdr[i].p_vaddr);
            // Виклик функції вилучення Build ID прямо з пам'яті
        }
    }
    return 0;
}

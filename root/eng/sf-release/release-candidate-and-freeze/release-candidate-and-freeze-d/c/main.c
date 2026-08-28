#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLASH_SECTOR_LIMIT_BYTES (8912896) /* 8.5 MiB */
#define RAM_LIMIT_BYTES          (393216)  /* 384 KiB */
#define STACK_GUARD_MIN_BYTES    (4096)    /* 4 KiB */

typedef struct {
    uint32_t text_size;
    uint32_t rodata_size;
    uint32_t data_size;
    uint32_t bss_size;
    uint32_t stack_min_free;
    uint32_t hil_failures_count;
    char git_commit_hash[41];
} FirmwareArtifactInfo;

typedef struct {
    bool is_approved;
    uint32_t total_flash_used;
    uint32_t total_ram_used;
    char error_message[128];
} ValidationReport;

ValidationReport validate_firmware_candidate(const FirmwareArtifactInfo* info) {
    ValidationReport report;
    memset(&report, 0, sizeof(ValidationReport));

    report.total_flash_used = info->text_size + info->rodata_size + info->data_size;
    report.total_ram_used = info->data_size + info->bss_size;

    if (info->hil_failures_count > 0) {
        report.is_approved = false;
        snprintf(report.error_message, sizeof(report.error_message),
                 "HIL верифікація містить %u збоїв", info->hil_failures_count);
        return report;
    }

    if (report.total_flash_used > FLASH_SECTOR_LIMIT_BYTES) {
        report.is_approved = false;
        snprintf(report.error_message, sizeof(report.error_message),
                 "Перевищено ліміт Flash: %u байт > %u байт",
                 report.total_flash_used, FLASH_SECTOR_LIMIT_BYTES);
        return report;
    }

    if (report.total_ram_used > RAM_LIMIT_BYTES) {
        report.is_approved = false;
        snprintf(report.error_message, sizeof(report.error_message),
                 "Перевищено ліміт SRAM: %u байт > %u байт",
                 report.total_ram_used, RAM_LIMIT_BYTES);
        return report;
    }

    if (info->stack_min_free < STACK_GUARD_MIN_BYTES) {
        report.is_approved = false;
        snprintf(report.error_message, sizeof(report.error_message),
                 "Небезпечний залишок стеку: %u байт < %u байт",
                 info->stack_min_free, STACK_GUARD_MIN_BYTES);
        return report;
    }

    report.is_approved = true;
    strncpy(report.error_message, "Всі критерії успішно виконано", sizeof(report.error_message) - 1);
    return report;
}

int main(void) {
    FirmwareArtifactInfo candidate = {
        .text_size = 3145728,    /* 3.0 MiB */
        .rodata_size = 524288,   /* 512 KiB */
        .data_size = 65536,      /* 64 KiB */
        .bss_size = 131072,      /* 128 KiB */
        .stack_min_free = 6144,  /* 6 KiB вільно */
        .hil_failures_count = 0,
        .git_commit_hash = "7f8b2c4e1a0d9f8e7c6b5a4d3e2f1a0b9c8d7e6f"
    };

    ValidationReport rep = validate_firmware_candidate(&candidate);

    printf("=== ЗВІТ ВАЛІДАЦІЇ РЕЛІЗ-КАНДИДАТА ===\n");
    printf("Flash ROM : %u / %u байт\n", rep.total_flash_used, FLASH_SECTOR_LIMIT_BYTES);
    printf("SRAM      : %u / %u байт\n", rep.total_ram_used, RAM_LIMIT_BYTES);
    printf("Статус    : %s\n", rep.is_approved ? "СХВАЛЕНО (READY FOR GA)" : "ВІДХИЛЕНО");
    printf("Деталі    : %s\n", rep.error_message);

    return rep.is_approved ? 0 : 1;
}

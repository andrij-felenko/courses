// cli_license.c — вивід ліцензійної таблиці з Flash у послідовну консоль
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    const char *component_name;
    const char *version;
    const char *spdx_license;
    const char *copyright_holder;
} FirmwareLicenseEntry;

// Таблиця прошитих компонентів (розміщується в секції .rodata у Flash)
static const FirmwareLicenseEntry FW_LICENSES[] = {
    { "FreeRTOS Kernel",       "10.5.1",  "MIT",          "Amazon.com, Inc. or its affiliates" },
    { "lwIP TCP/IP Stack",     "2.2.0",   "BSD-3-Clause", "Swedish Institute of Computer Science" },
    { "mbed TLS",              "3.4.1",   "Apache-2.0",   "TrustedFirmware.org" },
    { "FatFS Module",          "R0.15",   "FatFS-Notice", "ChaN" },
    { "ARM CMSIS Core & DSP",  "5.9.0",   "Apache-2.0",   "Arm Limited" },
    { "STM32CubeH7 HAL",       "1.11.0",  "BSD-3-Clause", "STMicroelectronics" },
    { "Wi-Fi PHY Driver",      "2.4.18",  "Proprietary",  "Silicon Vendor Corp" },
    { "Flight Autopilot Core", "3.2.0",   "Proprietary",  "Aerospace Dynamics Inc." }
};

static const size_t FW_LICENSES_COUNT = sizeof(FW_LICENSES) / sizeof(FW_LICENSES[0]);

void cli_cmd_print_licenses(void (*print_fn)(const char *str)) {
    char buf[128];
    print_fn("\r\n=== СПИСОК КОМПОНЕНТІВ ТА ЛІЦЕНЗІЙ ПРОШИВКИ (SBOM) ===\r\n");
    print_fn("Назва                    Версія   Ліцензія     Власник копірайту\r\n");
    print_fn("------------------------------------------------------------------------\r\n");

    for (size_t i = 0; i < FW_LICENSES_COUNT; ++i) {
        const FirmwareLicenseEntry *e = &FW_LICENSES[i];
        snprintf(buf, sizeof(buf), "%-24s %-8s %-12s %s\r\n",
                 e->component_name, e->version, e->spdx_license, e->copyright_holder);
        print_fn(buf);
    }
    print_fn("------------------------------------------------------------------------\r\n");
    print_fn("Повний текст ліцензій доступний за запитом або в інструкції користувача.\r\n\r\n");
}

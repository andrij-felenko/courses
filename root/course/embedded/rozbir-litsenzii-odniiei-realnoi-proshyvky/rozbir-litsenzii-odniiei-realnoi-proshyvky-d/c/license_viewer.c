// license_viewer.c — реалізація команди виводу ліцензій через послідовний інтерфейс
#include <stdint.h>
#include <stdio.h>

typedef struct {
    const char *module;
    const char *version;
    const char *license_type;
    const char *copyright;
} ComponentLicense;

// Таблиця атрибуції у Flash-пам'яті
static const ComponentLicense EMBEDDED_SBOM[] = {
    { "FreeRTOS Kernel",   "10.5.1",  "MIT",          "Amazon.com, Inc." },
    { "lwIP TCP/IP Stack", "2.2.0",   "BSD-3-Clause", "Swedish Institute of Computer Science" },
    { "mbed TLS",          "3.4.1",   "Apache-2.0",   "TrustedFirmware.org" },
    { "ARM CMSIS Core",    "5.9.0",   "Apache-2.0",   "Arm Limited" },
    { "STM32Cube HAL",     "1.11.0",  "BSD-3-Clause", "STMicroelectronics" },
    { "Madgwick AHRS",     "1.2.0",   "MIT",          "Sebastian Madgwick" }
};

static const size_t SBOM_SIZE = sizeof(EMBEDDED_SBOM) / sizeof(EMBEDDED_SBOM[0]);

void print_system_licenses(void (*write_uart)(const char *msg)) {
    char line[120];
    write_uart("\r\n--- ПАСПОРТ СТОРОННІХ КОМПОНЕНТІВ ПРОШИВКИ ---\r\n");
    for (size_t i = 0; i < SBOM_SIZE; ++i) {
        const ComponentLicense *c = &EMBEDDED_SBOM[i];
        snprintf(line, sizeof(line), "[%-16s v%-7s] %-12s (c) %s\r\n",
                 c->module, c->version, c->license_type, c->copyright);
        write_uart(line);
    }
    write_uart("Повні тексти ліцензій: https://vendor.example.com/legal/licenses\r\n\r\n");
}

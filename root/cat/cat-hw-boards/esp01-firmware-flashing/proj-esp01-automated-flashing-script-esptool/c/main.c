#include "esp01_uart.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    const char *port_path = "/dev/ttyUSB0";
    if (argc > 1) {
        port_path = argv[1];
    }

    printf("=== Системний драйвер діагностики ESP-01 (C POSIX UART) ===\n");
    printf("Ініціалізація послідовного порту: %s ...\n", port_path);

    esp01_config_t config = {
        .port_name = port_path,
        .baud_rate = 115200,
        .timeout_ms = 2000
    };

    esp01_driver_t driver;
    esp01_err_t err = esp01_init(&driver, &config);
    if (err != ESP01_OK) {
        fprintf(stderr, "[ПОМИЛКА] Не вдалося ініціалізувати порт %s (Код: %d)\n", port_path, err);
        return EXIT_FAILURE;
    }

    printf("[УСПІХ] Порт %s відкрито. Перевірка зв'язку з модулем ESP-01 (AT Ping)...\n", port_path);

    esp01_status_t status;
    err = esp01_get_status(&driver, &status);
    if (err == ESP01_OK && status.is_connected) {
        printf("\n--- Звіт діагностики стану ESP-01 ---\n");
        printf("Статус підключення : ДІЄВИЙ (Отримано відповідь OK)\n");
        printf("Готовність системи : %s\n", status.is_ready ? "ГОТОВИЙ ДО РОБОТИ" : "НЕ ГОТОВИЙ");
        printf("Версія прошивки    :\n%s\n", status.firmware_rev);
        printf("------------------------------------\n");
    } else {
        printf("[ПОМИЛКА] Модуль ESP-01 не відповідає на AT-команди. Перевірте лінії RX/TX та режим завантаження.\n");
    }

    esp01_close(&driver);
    printf("Файловий дескриптор закритий. Завершення роботи.\n");
    return EXIT_SUCCESS;
}

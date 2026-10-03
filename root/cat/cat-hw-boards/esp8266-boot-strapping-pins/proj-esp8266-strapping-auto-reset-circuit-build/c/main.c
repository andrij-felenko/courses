#include <stdio.h>
#include <stdbool.h>
#include "esp8266_boot_pins.h"

static void print_pins_diagram(const boot_pins_status_t *status) {
    printf("\n=== СТАН КОНФІГУРАЦІЙНИХ ВИВОДІВ ЗАВАНТАЖЕННЯ (BOOT STRAPPING PINS) ===\n");
    printf(" Сирий вміст регістра GPIO_IN: 0x%08X\n", status->raw_gpio_in);
    printf(" -----------------------------------------------------------------------\n");
    printf(" | Вивід  | Логічний рівень | Очікується для Flash Boot | Поточний стан |\n");
    printf(" -----------------------------------------------------------------------\n");
    printf(" | GPIO15 |        %d        |             0             |      %s      |\n",
           status->gpio15_level, status->gpio15_level == 0 ? " OK " : "FAIL");
    printf(" | GPIO0  |        %d        |             1             |      %s      |\n",
           status->gpio0_level, status->gpio0_level == 1 ? " OK " : "WARN");
    printf(" | GPIO2  |        %d        |             1             |      %s      |\n",
           status->gpio2_level, status->gpio2_level == 1 ? " OK " : "FAIL");
    printf(" -----------------------------------------------------------------------\n");
}

int main(void) {
    printf("========================================================================\n");
    printf("   ESP8266 Boot-Strapping Pins Verification & Diagnostic Module (C)    \n");
    printf("========================================================================\n");

    // Ініціалізація конфігурації за замовчуванням
    boot_pins_config_t config;
    esp8266_boot_pins_default_config(&config);
    config.sample_count = 10;

    // Опитування виводів завантаження
    boot_pins_status_t status = esp8266_read_boot_pins(&config);

    // Виведення результатів діагностики
    print_pins_diagram(&status);

    printf("\n[РЕЗУЛЬТАТ ДЕКОДУВАННЯ РЕЖИМУ]:\n -> %s\n", esp8266_boot_mode_to_str(status.mode));

    // Верифікація режима завантаження
    if (status.mode == BOOT_MODE_FLASH) {
        printf("\n[ВЕРИФІКАЦІЯ УСПІШНА]: Апаратні підтяжки налаштовано вірно для завантаження з SPI Flash.\n");
    } else if (status.mode == BOOT_MODE_UART) {
        printf("\n[ПОПЕРЕДЖЕННЯ]: Детектовано режим UART Download (GPIO0 затягнуто до GND).\n");
        printf("                Використовується для прошивання. Нормальне виконання призупинено.\n");
    } else if (status.mode == BOOT_MODE_SDIO) {
        printf("\n[УВАГА]: Детектовано SDIO Boot (GPIO15 затягнуто до VCC).\n");
    } else {
        printf("\n[КРИТИЧНА ПОМИЛКА]: Некоректний стан виводів (GPIO2 = 0 або GPIO15 = 1).\n");
        printf("                    Мікроконтролер може потрапити в циклічний перезапуск (bootloop)!\n");
    }

    // Демонстрація безпечного перевикористання виводів після завантаження
    printf("\n=== БЕЗПЕЧНЕ ПЕРЕВИКОРИСТАННЯ КОНФІГУРАЦІЙНИХ ВИВОДІВ ЯК ПЕРИФЕРІЇ ===\n");
    printf("Примітка: Переконайся, що зовнішнє периферійне обладнання не порушує підтяжки під час RESET.\n\n");

    // Переналаштування GPIO2 під світлодіод
    if (esp8266_reconfigure_pin_safe(2, true, false)) {
        printf("[OK] GPIO2 успішно переналаштовано як вихід (LED LOW).\n");
    }

    // Переналаштування GPIO0 під кнопковий вхід
    if (esp8266_reconfigure_pin_safe(0, false, false)) {
        printf("[OK] GPIO0 успішно переналаштовано як вхід кнопки.\n");
    }

    printf("\nЗавершення діагностичного модуля.\n");
    return 0;
}

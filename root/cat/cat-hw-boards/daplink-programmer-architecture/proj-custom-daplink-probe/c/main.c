#include "daplink_board.h"
#include <stdbool.h>

// Прототипи функцій з інших драйверів
void gpio_driver_init(void);
void gpio_set_nreset(bool assert_reset);
void usb_driver_init(void);
bool usb_rx_pop(uint8_t *packet);
bool usb_tx_send(const uint8_t *packet);
void swd_line_reset(void);

// Обробка команд протоколу CMSIS-DAP v1/v2
static void process_cmsis_dap_command(const uint8_t *cmd, uint8_t *resp) {
    resp[0] = cmd[0]; // Ехо ID команди

    switch (cmd[0]) {
        case 0x00: // DAP_Info
            resp[1] = 0x04; // Довжина відповіді
            resp[2] = 'D'; resp[3] = 'A'; resp[4] = 'P'; resp[5] = 0;
            break;

        case 0x02: // DAP_Connect
            swd_line_reset();
            resp[1] = 0x01; // SWD Mode підтверджено
            break;

        case 0x03: // DAP_Disconnect
            gpio_set_nreset(false);
            resp[1] = 0x00; // Success
            break;

        case 0x10: // DAP_ResetTarget
            gpio_set_nreset(true);
            // Затримка утримання скидання
            for (volatile int i = 0; i < 10000; i++);
            gpio_set_nreset(false);
            resp[1] = 0x00; // Success
            break;

        default:
            resp[1] = 0xFF; // Непідтримувана команда
            break;
    }
}

// Точка входу прошивки DAPLink для STM32F103
int main(void) {
    // 1. Ініціалізація апаратних периферійних модулів
    gpio_driver_init();
    usb_driver_init();

    uint8_t rx_packet[64];
    uint8_t tx_packet[64];

    // 2. Головний цикл обробки USB-команд та управління шиною SWD
    while (1) {
        // Перевіряємо наявність нових команд від розробницької станції
        if (usb_rx_pop(rx_packet)) {
            // Розбираємо команду CMSIS-DAP та формуємо відповідь
            process_cmsis_dap_command(rx_packet, tx_packet);

            // Відправляємо статус та дані назад хосту через USB
            usb_tx_send(tx_packet);
        }
    }

    return 0;
}

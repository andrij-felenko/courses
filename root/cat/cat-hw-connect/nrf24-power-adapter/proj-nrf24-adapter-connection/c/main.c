#include <stdint.h>
#include <stdio.h>
#include "nrf24_regs.h"

/* Приклад для мікроконтролерів із HAL (подібно до STM32).
   У реальному проєкті тут підключаються бібліотеки платформи. */

/* Заглушки функцій апаратного рівня */
extern void HAL_Delay(uint32_t ms);
extern uint8_t HAL_SPI_TransmitReceive(uint8_t *txData, uint8_t *rxData, uint16_t size, uint32_t timeout);
extern void HAL_GPIO_WritePin(void* GPIOx, uint16_t GPIO_Pin, int PinState);

#define CSN_PORT  ((void*)0x40020000)
#define CSN_PIN   0x0001
#define PIN_RESET 0
#define PIN_SET   1

/* Функція для керування піном CSN (Chip Select Not) */
void nrf24_set_csn(int state) {
    HAL_GPIO_WritePin(CSN_PORT, CSN_PIN, state);
}

/* Читання регістру nRF24L01 */
uint8_t nrf24_read_register(uint8_t reg) {
    uint8_t tx_buf[2];
    uint8_t rx_buf[2];
    
    /* Команда читання: базовий байт + адреса регістру (5 молодших біт) */
    tx_buf[0] = NRF24_CMD_R_REGISTER | (reg & 0x1F);
    tx_buf[1] = NRF24_CMD_NOP; /* Пустий байт для отримання даних */
    
    /* Опускаємо CSN для початку транзакції */
    nrf24_set_csn(PIN_RESET);
    
    /* Передаємо команду та одночасно приймаємо відповідь */
    HAL_SPI_TransmitReceive(tx_buf, rx_buf, 2, 100);
    
    /* Підіймаємо CSN для завершення транзакції */
    nrf24_set_csn(PIN_SET);
    
    /* Повертаємо отримане значення (другий байт) */
    return rx_buf[1];
}

int main(void) {
    /* Ініціалізація периферії (SPI, GPIO) */
    /* HAL_Init(); */
    
    /* Затримка на стабілізацію живлення адаптера після старту */
    HAL_Delay(100);
    
    /* Піднімаємо CSN (вимкнений стан, активний низький) */
    nrf24_set_csn(PIN_SET);
    
    /* Тестове читання регістру STATUS */
    uint8_t status = nrf24_read_register(NRF24_REG_STATUS);
    
    /* Перевірка зв'язку: за замовчуванням після скидання STATUS не 0x00 і не 0xFF.
       Якщо отримано 0x00 або 0xFF - ймовірні проблеми з живленням або лініями SPI */
    printf("Отриманий статус: 0x%02X\n", status);
    
    while (1) {
        /* Основний цикл програми */
    }
    
    return 0;
}

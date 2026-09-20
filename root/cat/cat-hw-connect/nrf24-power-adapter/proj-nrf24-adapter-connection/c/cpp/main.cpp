#include <cstdint>
#include <iostream>
#include "Nrf24l01.hpp"

/* Заглушки апаратних функцій */
extern void HAL_Delay(uint32_t ms);
extern void HW_SPI_Transfer(const uint8_t* tx, uint8_t* rx, uint16_t len);
extern void HW_CSN_Write(bool active);

/* Реалізація інтерфейсу для обміну даними через SPI */
void spiTransferImpl(const uint8_t* txData, uint8_t* rxData, uint16_t size) {
    HW_SPI_Transfer(txData, rxData, size);
}

/* Реалізація керування піном CSN */
void csnControlImpl(bool active) {
    /* nRF24L01 активується низьким рівнем (Active LOW) */
    HW_CSN_Write(active ? false : true);
}

int main() {
    /* Ініціалізація периферії мікроконтролера */
    /* HW_Init(); */
    
    /* Затримка для стабілізації живлення адаптера nRF24 */
    HAL_Delay(100);

    /* Створення об'єкта для керування радіомодулем.
       Залежності передаються явно для простоти тестування і зміни платформи. */
    Nrf24l01 radio(spiTransferImpl, csnControlImpl);

    /* Спроба зв'язатися з модулем та прочитати STATUS регістр */
    if (radio.begin()) {
        std::cout << "Успіх: nRF24L01 виявлено. Адаптер працює стабільно.\n";
        
        /* Читання статусу як доказ роботи */
        uint8_t status = radio.readRegister(0x07);
        std::cout << "STATUS: 0x" << std::hex << (int)status << "\n";
    } else {
        std::cout << "Помилка: Модуль не знайдено. Перевірте SPI та живлення адаптера.\n";
    }

    while (true) {
        /* Головний цикл */
    }

    return 0;
}

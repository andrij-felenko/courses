#include "Nrf24l01.hpp"

Nrf24l01::Nrf24l01(SpiTransferFunc spiTransfer, CsnControlFunc csnControl)
    : spiTransfer_(spiTransfer), csnControl_(csnControl) {
}

bool Nrf24l01::begin() {
    /* Забезпечуємо неактивний стан CSN перед початком обміну */
    csnControl_(false);
    
    /* Читаємо статус для перевірки підключення і живлення */
    uint8_t status = readRegister(REG_STATUS);
    
    /* 0x00 або 0xFF зазвичай свідчать про обрив зв'язку або відсутність живлення */
    if (status == 0x00 || status == 0xFF) {
        return false;
    }
    
    return true;
}

uint8_t Nrf24l01::readRegister(uint8_t reg) {
    uint8_t txData[2];
    uint8_t rxData[2] = {0};

    txData[0] = CMD_R_REGISTER | (reg & 0x1F);
    txData[1] = CMD_NOP;

    /* Активація транзакції (CSN = LOW) */
    csnControl_(true);

    /* Синхронна передача і прийом двох байтів */
    spiTransfer_(txData, rxData, 2);

    /* Завершення транзакції (CSN = HIGH) */
    csnControl_(false);

    /* Перший байт у rxData містить статус, другий — значення регістру */
    return rxData[1];
}

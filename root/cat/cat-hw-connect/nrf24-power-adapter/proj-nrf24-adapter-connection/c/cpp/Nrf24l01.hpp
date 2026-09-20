#pragma once
#include <cstdint>

class Nrf24l01 {
public:
    using SpiTransferFunc = void(*)(const uint8_t* txData, uint8_t* rxData, uint16_t size);
    using CsnControlFunc = void(*)(bool active);

    Nrf24l01(SpiTransferFunc spiTransfer, CsnControlFunc csnControl);

    /* Ініціалізує початковий стан і перевіряє наявність модуля */
    bool begin();

    /* Читає значення вказаного регістру */
    uint8_t readRegister(uint8_t reg);

private:
    SpiTransferFunc spiTransfer_;
    CsnControlFunc csnControl_;

    static constexpr uint8_t CMD_R_REGISTER = 0x00;
    static constexpr uint8_t CMD_NOP        = 0xFF;

    static constexpr uint8_t REG_STATUS     = 0x07;
};

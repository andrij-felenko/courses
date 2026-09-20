#include "cc1101.h"

// Фіктивні функції HAL для SPI та затримок, 
// які в реальному проєкті реалізовані платформою.
extern void SPI_Select(void);
extern void SPI_Deselect(void);
extern uint8_t SPI_Transfer(uint8_t data);
extern void Delay_ms(uint32_t ms);

void CC1101_WriteReg(uint8_t addr, uint8_t value) {
    SPI_Select();
    SPI_Transfer(addr);
    SPI_Transfer(value);
    SPI_Deselect();
}

uint8_t CC1101_ReadReg(uint8_t addr) {
    SPI_Select();
    SPI_Transfer(addr | 0x80); // Біт читання
    uint8_t val = SPI_Transfer(0x00);
    SPI_Deselect();
    return val;
}

void CC1101_Strobe(uint8_t cmd) {
    SPI_Select();
    SPI_Transfer(cmd);
    SPI_Deselect();
}

void CC1101_Reset(void) {
    SPI_Select();
    Delay_ms(1);
    SPI_Deselect();
    Delay_ms(1);
    
    CC1101_Strobe(CC1101_SRES);
}

void CC1101_Init(void) {
    CC1101_Reset();
    
    // Тут мало б бути налаштування регістрів для 433 МГц, швидкості, девіації тощо.
    // Записуємо мінімально необхідне для прикладу.
    CC1101_WriteReg(0x0B, 0x06); // FSCTRL1
    CC1101_WriteReg(0x0C, 0x00); // FSCTRL0
    // ... інші регістри ...
}

void CC1101_SendPacket(const CC1101_Packet *pkt) {
    CC1101_SetIdle();
    CC1101_Strobe(CC1101_SFLUSHTX);
    
    SPI_Select();
    SPI_Transfer(CC1101_FIFO);
    SPI_Transfer(pkt->length); // Відправляємо довжину пакета
    for (uint8_t i = 0; i < pkt->length; i++) {
        SPI_Transfer(pkt->data[i]);
    }
    SPI_Deselect();
    
    CC1101_Strobe(CC1101_STX); // Запуск передавання
}

bool CC1101_ReceivePacket(CC1101_Packet *pkt) {
    uint8_t rxBytes = CC1101_ReadReg(0x3B | 0xC0); // Читання RXBYTES
    
    if (rxBytes > 0) {
        pkt->length = CC1101_ReadReg(CC1101_FIFO);
        if (pkt->length <= 64 && pkt->length > 0) {
            SPI_Select();
            SPI_Transfer(CC1101_FIFO | 0x80); // Бурстове читання
            for (uint8_t i = 0; i < pkt->length; i++) {
                pkt->data[i] = SPI_Transfer(0x00);
            }
            SPI_Deselect();
            
            CC1101_SetIdle();
            CC1101_Strobe(CC1101_SFLUSHRX);
            return true;
        } else {
            // Помилка розміру пакета
            CC1101_SetIdle();
            CC1101_Strobe(CC1101_SFLUSHRX);
            return false;
        }
    }
    return false;
}

void CC1101_SetIdle(void) {
    CC1101_Strobe(CC1101_SIDLE);
    while (CC1101_ReadReg(CC1101_MARCSTATE) != 0x01) {
        // Очікування переходу в IDLE
    }
}

void CC1101_SetRx(void) {
    CC1101_SetIdle();
    CC1101_Strobe(CC1101_SRX);
}

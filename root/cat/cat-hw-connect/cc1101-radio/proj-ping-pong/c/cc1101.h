#ifndef CC1101_H
#define CC1101_H

#include <stdint.h>
#include <stdbool.h>

// Основні регістри та команди (strobe)
#define CC1101_SRES     0x30 // Скидання
#define CC1101_SFSTXON  0x31 // Увімкнути калібрування синтезатора
#define CC1101_SXOFF    0x32 // Вимкнути кварцовий генератор
#define CC1101_SCAL     0x33 // Калібрування
#define CC1101_SRX      0x34 // Перехід у режим приймання (RX)
#define CC1101_STX      0x35 // Перехід у режим передавання (TX)
#define CC1101_SIDLE    0x36 // Перехід у режим очікування (IDLE)
#define CC1101_SFLUSHRX 0x3A // Очистити буфер RX
#define CC1101_SFLUSHTX 0x3B // Очистити буфер TX

#define CC1101_FIFO     0x3F // Регістр доступу до FIFO

// Регістри статусу
#define CC1101_MARCSTATE 0xF5 // Стан скінченного автомата

// Структура для пакету даних
typedef struct {
    uint8_t length;
    uint8_t data[64];
} CC1101_Packet;

// Прототипи функцій драйвера
void CC1101_Init(void);
void CC1101_Reset(void);
void CC1101_WriteReg(uint8_t addr, uint8_t value);
uint8_t CC1101_ReadReg(uint8_t addr);
void CC1101_Strobe(uint8_t cmd);
void CC1101_SendPacket(const CC1101_Packet *pkt);
bool CC1101_ReceivePacket(CC1101_Packet *pkt);
void CC1101_SetIdle(void);
void CC1101_SetRx(void);

#endif // CC1101_H

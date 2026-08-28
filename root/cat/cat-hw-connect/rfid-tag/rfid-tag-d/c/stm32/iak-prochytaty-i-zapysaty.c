#include "main.h"
#include <stdio.h>

extern SPI_HandleTypeDef  hspi1;     // SPI1 на читач; вибір кристала смикаємо самі
extern UART_HandleTypeDef huart2;

#define CS_LOW()   HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET)
#define CS_HIGH()  HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET)

// адресний байт MFRC522: (reg<<1)&0x7E; старший біт 1 — читання, 0 — запис
static void wr(uint8_t reg, uint8_t v) {
    uint8_t tx[2] = { (uint8_t)((reg << 1) & 0x7E), v };
    CS_LOW();  HAL_SPI_Transmit(&hspi1, tx, 2, HAL_MAX_DELAY);  CS_HIGH();
}
static uint8_t rd(uint8_t reg) {
    uint8_t tx[2] = { (uint8_t)(0x80 | ((reg << 1) & 0x7E)), 0 }, rx[2] = { 0 };
    CS_LOW();  HAL_SPI_TransmitReceive(&hspi1, tx, rx, 2, HAL_MAX_DELAY);  CS_HIGH();
    return rx[1];
}

// один обмін із міткою: байти у FIFO → команда Transceive → відповідь із FIFO
static int transceive(const uint8_t *tx, int n, uint8_t lastbits, uint8_t *rx, int max) {
    wr(0x01, 0x00); wr(0x04, 0x7F); wr(0x0A, 0x80);  // Idle, скинути IRQ, чистити FIFO
    for (int i = 0; i < n; i++) wr(0x09, tx[i]);     // FIFODataReg
    wr(0x01, 0x0C);                                  // CommandReg = Transceive
    wr(0x0D, 0x80 | lastbits);                       // BitFramingReg: StartSend
    for (int i = 0; i < 20 && !(rd(0x04) & 0x30); i++) HAL_Delay(1);
    wr(0x0D, 0x00);
    int len = rd(0x0A);                              // скільки байтів прийшло у FIFO
    if (len > max) len = max;
    for (int i = 0; i < len; i++) rx[i] = rd(0x09);
    return len;
}

static void pcd_init(void) {                         // те, що робить PCD_Init()
    wr(0x01, 0x0F); HAL_Delay(50);                   // SoftReset
    wr(0x2A, 0x8D); wr(0x2B, 0x3E); wr(0x2D, 30); wr(0x2C, 0);  // таймер ~25 мс
    wr(0x15, 0x40);                                  // TxASKReg: 100 % ASK
    wr(0x11, 0x3D);                                  // ModeReg: преднастройка CRC
    wr(0x14, rd(0x14) | 0x03);                       // TxControlReg: увімкнути антену
}

int main(void) {
    HAL_Init();  SystemClock_Config();
    MX_GPIO_Init();  MX_SPI1_Init();  MX_USART2_UART_Init();
    pcd_init();

    while (1) {
        uint8_t reqa = 0x26, atqa[2], uid[5], line[40];
        if (transceive(&reqa, 1, 7, atqa, 2) == 2) {        // REQA — кадр завдовжки 7 біт
            uint8_t anti[2] = { 0x93, 0x20 };               // антиколізія, каскад 1
            if (transceive(anti, 2, 0, uid, 5) == 5) {      // 4 байти UID + байт BCC
                int k = snprintf((char *)line, sizeof line, "UID: %02X %02X %02X %02X\r\n",
                                 uid[0], uid[1], uid[2], uid[3]);
                HAL_UART_Transmit(&huart2, line, k, HAL_MAX_DELAY);
            }
        }
        HAL_Delay(200);
    }
}

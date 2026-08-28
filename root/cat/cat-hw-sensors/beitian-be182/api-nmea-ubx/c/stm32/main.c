// Побудувати кадр UBX-CFG-VALSET і надіслати в модуль (STM32 HAL, USART1).
#include "stm32f4xx_hal.h"

extern UART_HandleTypeDef huart1;                  // порт, до якого підключено BE-182

// Ключі конфігурації u-blox M10 (з опису інтерфейсу):
#define CFG_RATE_MEAS      0x30210001UL            // період вимірів, мс   (U2)
#define CFG_UART1_BAUDRATE 0x40520001UL            // швидкість UART1      (U4)

HAL_StatusTypeDef ubx_valset(uint32_t key, uint32_t value, uint8_t vlen)
{
    uint8_t f[64];
    uint16_t n = 0;
    f[n++] = 0xB5; f[n++] = 0x62;                  // синхросимволи
    f[n++] = 0x06; f[n++] = 0x8A;                  // клас, номер: CFG-VALSET
    uint16_t plen = 4 + 4 + vlen;                  // заголовок(4) + ключ(4) + значення
    f[n++] = plen & 0xFF; f[n++] = plen >> 8;      // довжина, молодший уперед
    f[n++] = 0x00;                                 // версія
    f[n++] = 0x01;                                 // шар: 0x01 = оперативна пам'ять
    f[n++] = 0x00; f[n++] = 0x00;                  // зарезервовано
    for (int i = 0; i < 4; i++)    f[n++] = (key   >> (8 * i)) & 0xFF;  // ключ, LE
    for (int i = 0; i < vlen; i++) f[n++] = (value >> (8 * i)) & 0xFF;  // значення, LE

    uint8_t ck_a = 0, ck_b = 0;                    // Флетчер: від класу до кінця даних
    for (uint16_t i = 2; i < n; i++) { ck_a += f[i]; ck_b += ck_a; }
    f[n++] = ck_a; f[n++] = ck_b;

    return HAL_UART_Transmit(&huart1, f, n, 100);  // 100 мс на віддачу кадру
}

void set_rate_10hz(void) { ubx_valset(CFG_RATE_MEAS, 100, 2); }   // 100 мс = 10 Гц

void set_baud_115200(void)                         // і одразу переїхати самому
{
    ubx_valset(CFG_UART1_BAUDRATE, 115200, 4);
    HAL_Delay(100);                                // дати модулю доказати на старій
    huart1.Init.BaudRate = 115200;
    HAL_UART_Init(&huart1);
}

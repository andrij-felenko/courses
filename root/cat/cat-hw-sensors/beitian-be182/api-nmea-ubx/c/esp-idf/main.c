// Побудувати кадр UBX-CFG-VALSET і надіслати в модуль (ESP-IDF, UART1).
#include "driver/uart.h"
#include "esp_log.h"

#define GNSS_UART  UART_NUM_1
static const char *TAG = "ubx";

// Ключі конфігурації u-blox M10 (з опису інтерфейсу):
#define CFG_RATE_MEAS      0x30210001UL            // період вимірів, мс   (U2)
#define CFG_UART1_BAUDRATE 0x40520001UL            // швидкість UART1      (U4)

esp_err_t ubx_valset(uint32_t key, uint32_t value, uint8_t vlen)
{
    uint8_t f[64];
    uint8_t n = 0;
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
    for (uint8_t i = 2; i < n; i++) { ck_a += f[i]; ck_b += ck_a; }
    f[n++] = ck_a; f[n++] = ck_b;

    int sent = uart_write_bytes(GNSS_UART, f, n);
    ESP_LOGI(TAG, "UBX key=0x%08X, надіслано %d Б", (unsigned)key, sent);
    return (sent == n) ? ESP_OK : ESP_FAIL;
}

void set_rate_10hz(void)   { ubx_valset(CFG_RATE_MEAS, 100, 2); }   // 100 мс = 10 Гц
void set_rate_1hz(void)    { ubx_valset(CFG_RATE_MEAS, 1000, 2); }  // 1000 мс = 1 Гц
void set_baud_115200(void) { ubx_valset(CFG_UART1_BAUDRATE, 115200, 4); }

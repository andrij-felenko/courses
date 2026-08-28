// Побудувати кадр UBX-CFG-VALSET і надіслати в модуль (Arduino, Serial1).
// key   — ключ конфігурації u-blox (напр. CFG-RATE-MEAS)
// value — нове значення; vlen — його довжина в байтах (2 або 4)
#include <stdint.h>

void ubx_valset(uint32_t key, uint32_t value, uint8_t vlen) {
    uint8_t body[64];
    uint8_t n = 0;
    body[n++] = 0x06; body[n++] = 0x8A;        // клас, номер: CFG-VALSET
    uint16_t plen = 4 + 4 + vlen;              // заголовок(4) + ключ(4) + значення
    body[n++] = plen & 0xFF; body[n++] = plen >> 8;   // довжина, молодший уперед
    body[n++] = 0x00;                          // версія
    body[n++] = 0x01;                          // шар: 0x01 = оперативна пам'ять
    body[n++] = 0x00; body[n++] = 0x00;        // зарезервовано
    for (int i = 0; i < 4; i++) body[n++] = (key   >> (8 * i)) & 0xFF;   // ключ, LE
    for (int i = 0; i < vlen; i++) body[n++] = (value >> (8 * i)) & 0xFF; // значення, LE

    // контрольна сума Флетчера: пробігти всі байти body
    uint8_t ck_a = 0, ck_b = 0;
    for (uint8_t i = 0; i < n; i++) { ck_a += body[i]; ck_b += ck_a; }

    Serial1.write(0xB5); Serial1.write(0x62);  // синхросимволи
    Serial1.write(body, n);                    // тіло
    Serial1.write(ck_a); Serial1.write(ck_b);  // сума
}

// Ключі конфігурації u-blox M10 (з опису інтерфейсу):
#define CFG_RATE_MEAS      0x30210001UL        // період вимірів, мс   (U2)
#define CFG_UART1_BAUDRATE 0x40520001UL        // швидкість UART1      (U4)

void set_rate_10hz()  { ubx_valset(CFG_RATE_MEAS, 100, 2); }   // 100 мс = 10 Гц
void set_rate_1hz()   { ubx_valset(CFG_RATE_MEAS, 1000, 2); }  // 1000 мс = 1 Гц
void set_baud_115200(){ ubx_valset(CFG_UART1_BAUDRATE, 115200, 4); }

#include <stdint.h>

/* Примітиви з кроку ініціалізації — ті самі, не переписуємо. */
void send_cmd(uint8_t c);                        // D/C = 0, вилити байт-команду
void send_data(const uint8_t *buf, uint32_t n);  // D/C = 1, вилити n байтів даних

#define CASET  0x2A   // column address set — межі стовпців
#define RASET  0x2B   // row address set    — межі рядків
#define RAMWR  0x2C   // memory write       — відкрити потік пікселів

/* Окреслити прямокутне вікно [x0..x1] × [y0..y1] і відкрити прийом пікселів.
   Межі ВКЛЮЧНІ з обох кінців: вікно 0..0 — це рівно один піксель. */
static void set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1)
{
    uint8_t buf[4];

    send_cmd(CASET);                    // далі — чотири байти меж стовпців
    buf[0] = (uint8_t)(x0 >> 8);        // x0 СТАРШИЙ байт першим
    buf[1] = (uint8_t)(x0 & 0xFF);      // x0 молодший
    buf[2] = (uint8_t)(x1 >> 8);        // x1 старший
    buf[3] = (uint8_t)(x1 & 0xFF);      // x1 молодший
    send_data(buf, 4);

    send_cmd(RASET);                    // те саме для рядків
    buf[0] = (uint8_t)(y0 >> 8);
    buf[1] = (uint8_t)(y0 & 0xFF);
    buf[2] = (uint8_t)(y1 >> 8);
    buf[3] = (uint8_t)(y1 & 0xFF);
    send_data(buf, 4);

    send_cmd(RAMWR);                    // курсор у (x0,y0), контролер чекає потік
}

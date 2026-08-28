#include "u8g2.h"

static u8g2_t u8g2;                 // структура дисплея; буфер 1024 Б — усередині
extern I2C_HandleTypeDef hi2c1;     // налаштований у CubeMX

// Колбек №1: віддати байти по I2C. U8g2 накопичує їх, а на END — шле пачку.
static uint8_t u8x8_byte_stm32_hw_i2c(u8x8_t *u8x8, uint8_t msg,
                                      uint8_t arg_int, void *arg_ptr) {
  static uint8_t buf[32];
  static uint8_t idx;
  uint8_t *data;
  switch (msg) {
    case U8X8_MSG_BYTE_START_TRANSFER: idx = 0; break;
    case U8X8_MSG_BYTE_SEND:
      data = (uint8_t *)arg_ptr;
      while (arg_int-- > 0) buf[idx++] = *data++;   // збираємо у свій буфер
      break;
    case U8X8_MSG_BYTE_END_TRANSFER:
      // 0x3C << 1 = 0x78 — HAL хоче 8-бітну адресу! (та сама каверза, що й у сканері)
      HAL_I2C_Master_Transmit(&hi2c1, 0x78, buf, idx, HAL_MAX_DELAY);
      break;
  }
  return 1;
}

// Колбек №2: затримки. Для I2C потрібні лише мілісекунди.
static uint8_t u8x8_gpio_and_delay_stm32(u8x8_t *u8x8, uint8_t msg,
                                         uint8_t arg_int, void *arg_ptr) {
  if (msg == U8X8_MSG_DELAY_MILLI) HAL_Delay(arg_int);
  return 1;
}

void oled_init(void) {
  // Конструктор «повнобуферного» (_f) драйвера саме SSD1306 128x64 noname.
  u8g2_Setup_ssd1306_i2c_128x64_noname_f(
      &u8g2, U8G2_R0,                       // R0 — без повороту
      u8x8_byte_stm32_hw_i2c, u8x8_gpio_and_delay_stm32);

  u8g2_InitDisplay(&u8g2);      // шле всю послідовність ініціалізації (насос теж!)
  u8g2_SetPowerSave(&u8g2, 0);  // 0 — прокинутися; 1 — приспати екран
  u8g2_ClearBuffer(&u8g2);

  u8g2_SetFont(&u8g2, u8g2_font_ncenB14_tr);
  u8g2_DrawStr(&u8g2, 0, 30, "Привіт!");
  u8g2_SendBuffer(&u8g2);       // ← аналог display(): без нього скло порожнє
}

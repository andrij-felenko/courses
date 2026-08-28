#include <string.h>
#include <stdio.h>
#include "main.h"                // HAL і hi2c1, згенеровані CubeMX
#include "u8g2.h"

extern I2C_HandleTypeDef hi2c1;
static u8g2_t u8g2;
#define SSD1306_ADDR (0x3C << 1) // HAL теж чекає адресу, зсунуту на біт R/W

typedef enum { ST_IDLE, ST_MEASURE, ST_ALARM, ST_CONFIG } hud_state_t;

static const char *state_name(hud_state_t s) {
  switch (s) {
    case ST_IDLE:    return "IDLE";
    case ST_MEASURE: return "MEASURE";
    case ST_ALARM:   return "ALARM";
    case ST_CONFIG:  return "CONFIG";
  }
  return "?";
}

static const char *MENU[] = { "Run", "Zero", "Rng", "Set" };
#define MENU_N 4

// Уся платформозалежність — у двох колбеках: байти в шину і пауза.
static uint8_t u8x8_hal_i2c(u8x8_t *u8x8, uint8_t msg, uint8_t len, void *arg) {
  static uint8_t buf[32], n;
  switch (msg) {
    case U8X8_MSG_BYTE_START_TRANSFER: n = 0; break;
    case U8X8_MSG_BYTE_SEND: memcpy(buf + n, arg, len); n += len; break;
    case U8X8_MSG_BYTE_END_TRANSFER:
      HAL_I2C_Master_Transmit(&hi2c1, SSD1306_ADDR, buf, n, HAL_MAX_DELAY);
      break;
    default: break;
  }
  return 1;
}
static uint8_t u8x8_hal_delay(u8x8_t *u8x8, uint8_t msg, uint8_t len, void *arg) {
  if (msg == U8X8_MSG_DELAY_MILLI) HAL_Delay(len);
  return 1;
}

static void draw_hud(hud_state_t st, int32_t centi, int cursor) {
  char s[16];
  u8g2_ClearBuffer(&u8g2);

  // — Зона 1: рядок стану вгорі, у рамці-плашці ————————————————
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);
  u8g2_DrawFrame(&u8g2, 0, 0, 128, 14);
  snprintf(s, sizeof(s), "St: %s", state_name(st));
  u8g2_DrawStr(&u8g2, 4, 11, s);                 // y — базова лінія рядка

  // — Зона 2: велике число посередині, ціле «з комою вручну» ————————
  int32_t whole = centi / 100;
  int32_t frac  = centi % 100;
  if (frac < 0) frac = -frac;
  snprintf(s, sizeof(s), "%ld.%02ld", (long)whole, (long)frac);
  u8g2_SetFont(&u8g2, u8g2_font_logisoso24_tn);
  u8g2_DrawStr(&u8g2, 6, 44, s);
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);
  u8g2_DrawStr(&u8g2, 104, 38, "C");

  // — Зона 3: рядок меню внизу, курсор «>» перед активним пунктом ——————
  u8g2_DrawHLine(&u8g2, 0, 50, 128);
  int x = 2;
  for (int i = 0; i < MENU_N; i++) {
    snprintf(s, sizeof(s), "%c%s", i == cursor ? '>' : ' ', MENU[i]);
    u8g2_DrawStr(&u8g2, x, 62, s);
    x += (strlen(MENU[i]) + 2) * 6;
  }

  u8g2_SendBuffer(&u8g2);                        // ← штовхаємо весь кадр на скло
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_I2C1_Init();                                // шину підняв CubeMX

  u8g2_Setup_ssd1306_i2c_128x64_noname_f(&u8g2, U8G2_R0, u8x8_hal_i2c, u8x8_hal_delay);
  u8g2_InitDisplay(&u8g2);
  u8g2_SetPowerSave(&u8g2, 0);

  int32_t t = 2500;
  int cursor = 0;
  for (;;) {
    t += 7;
    hud_state_t st = (t > 8000) ? ST_ALARM : ST_MEASURE;
    draw_hud(st, t, cursor);
    cursor = (cursor + 1) % MENU_N;
    HAL_Delay(400);
  }
}

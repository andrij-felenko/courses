#include <string.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/i2c.h"          // шину тримає драйвер IDF
#include "u8g2.h"
#include "u8g2_esp32_hal.h"      // порт u8g2 під ESP-IDF: колбеки на driver/i2c

static const char *TAG = "hud";
static u8g2_t u8g2;

typedef enum { ST_IDLE, ST_MEASURE, ST_ALARM, ST_CONFIG } hud_state_t;

// Людські назви станів для верхнього рядка.
static const char *state_name(hud_state_t s) {
  switch (s) {
    case ST_IDLE:    return "IDLE";
    case ST_MEASURE: return "MEASURE";
    case ST_ALARM:   return "ALARM";
    case ST_CONFIG:  return "CONFIG";
  }
  return "?";
}

static const char *MENU[] = { "Run", "Zero", "Rng", "Set" };  // підписи КОРОТКІ навмисне
#define MENU_N 4

// Намалювати ВЕСЬ кадр за поточним станом.
static void draw_hud(hud_state_t st, int32_t centi, int cursor) {
  char s[16];
  u8g2_ClearBuffer(&u8g2);                       // чистимо буфер, малюємо кадр з нуля

  // — Зона 1: рядок стану вгорі, у рамці-плашці ————————————————
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);        // у u8g2 розмір задає САМ шрифт
  u8g2_DrawFrame(&u8g2, 0, 0, 128, 14);
  snprintf(s, sizeof(s), "St: %s", state_name(st));
  u8g2_DrawStr(&u8g2, 4, 11, s);                 // y — БАЗОВА лінія, не верх рядка

  // — Зона 2: велике число посередині, ціле «з комою вручну» ————————
  int32_t whole = centi / 100;                   // ціла частина
  int32_t frac  = centi % 100;                   // дві цифри після коми
  if (frac < 0) frac = -frac;                    // модуль, щоб «-1.05» не став «-1.-5»
  snprintf(s, sizeof(s), "%ld.%02ld", (long)whole, (long)frac);
  u8g2_SetFont(&u8g2, u8g2_font_logisoso24_tn);  // «велику цифру» дає великий шрифт
  u8g2_DrawStr(&u8g2, 6, 44, s);
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);        // одиниці — дрібним, у куточку
  u8g2_DrawStr(&u8g2, 104, 38, "C");

  // — Зона 3: рядок меню внизу, курсор «>» перед активним пунктом ——————
  u8g2_DrawHLine(&u8g2, 0, 50, 128);             // відділити меню лінією
  int x = 2;
  for (int i = 0; i < MENU_N; i++) {
    snprintf(s, sizeof(s), "%c%s", i == cursor ? '>' : ' ', MENU[i]);
    u8g2_DrawStr(&u8g2, x, 62, s);
    x += (strlen(MENU[i]) + 2) * 6;              // той самий пікселний бюджет: 6 px на символ
  }

  u8g2_SendBuffer(&u8g2);                        // ← штовхаємо весь кадр на скло
}

void app_main(void) {
  u8g2_esp32_hal_t hal = U8G2_ESP32_HAL_DEFAULT; // глей: які саме виводи несуть шину
  hal.bus.i2c.sda = GPIO_NUM_21;
  hal.bus.i2c.scl = GPIO_NUM_22;
  u8g2_esp32_hal_init(hal);

  u8g2_Setup_ssd1306_i2c_128x64_noname_f(&u8g2, U8G2_R0,
      u8g2_esp32_i2c_byte_cb, u8g2_esp32_gpio_and_delay_cb);
  u8x8_SetI2CAddress(&u8g2.u8x8, 0x3C << 1);     // адреса, зсунута на біт R/W
  u8g2_InitDisplay(&u8g2);
  u8g2_SetPowerSave(&u8g2, 0);                   // прокинути скло після ініціалізації
  ESP_LOGI(TAG, "SSD1306 готовий");

  int32_t t = 2500;                              // 25.00 °C у сотих
  int cursor = 0;
  for (;;) {
    t += 7;                                      // «давач» поволі росте
    hud_state_t st = (t > 8000) ? ST_ALARM : ST_MEASURE;
    draw_hud(st, t, cursor);                     // перемалювали кадр
    cursor = (cursor + 1) % MENU_N;              // курсор на наступний пункт
    vTaskDelay(pdMS_TO_TICKS(400));              // ← не delay(): віддаємо час планувальнику
  }
}

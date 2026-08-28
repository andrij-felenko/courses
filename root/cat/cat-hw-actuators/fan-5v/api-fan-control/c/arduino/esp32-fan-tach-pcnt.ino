// esp32-fan-tach-pcnt.ino — оберти через апаратний лічильник PCNT (ESP-IDF 5.x driver)
#include <Arduino.h>
#include "driver/pulse_cnt.h"

const int TACH_PIN = 27;
pcnt_unit_handle_t    unit = nullptr;    // дескриптор лічильника
pcnt_channel_handle_t chan = nullptr;    // дескриптор каналу

void tachPcntBegin() {
  // 1. Юніт-лічильник із межами (16-бітний: −32768…32767)
  pcnt_unit_config_t unit_cfg = {
    .low_limit  = -1,                    // мінімум трохи нижче нуля (вимога API)
    .high_limit =  32767,                // стеля 16-бітного лічильника
  };
  pcnt_new_unit(&unit_cfg, &unit);

  // 2. Канал: стежити за фронтами саме на виводі TACH
  pcnt_chan_config_t chan_cfg = {
    .edge_gpio_num  = TACH_PIN,          // тут блок лічить фронти
    .level_gpio_num = -1,                // рівень-керування не потрібне
  };
  pcnt_new_channel(unit, &chan_cfg, &chan);

  // 3. На висхідному фронті — +1, на низхідному — нічого (один імпульс = +1)
  pcnt_channel_set_edge_action(chan,
      PCNT_CHANNEL_EDGE_ACTION_INCREASE,     // висхідний фронт
      PCNT_CHANNEL_EDGE_ACTION_HOLD);        // низхідний фронт

  // 4. Фільтр голок: усе коротше за 1 мкс — шум, ігноруємо
  pcnt_glitch_filter_config_t filt = { .max_glitch_ns = 1000 };
  pcnt_unit_set_glitch_filter(unit, &filt);

  // 5. Увімкнути → обнулити → запустити
  pcnt_unit_enable(unit);
  pcnt_unit_clear_count(unit);
  pcnt_unit_start(unit);
}

void setup() {
  Serial.begin(115200);
  pinMode(TACH_PIN, INPUT_PULLUP);       // підтяжка все одно потрібна — сигнал OC
  tachPcntBegin();
}

uint32_t lastMs = 0;
void loop() {
  uint32_t now = millis();
  if (now - lastMs >= 1000) {            // вимірюємо рівно за секунду
    lastMs = now;
    int count = 0;
    pcnt_unit_get_count(unit, &count);   // залізо вже все порахувало
    pcnt_unit_clear_count(unit);         // скид на новий інтервал

    uint32_t rpm = (count / 2) * 60;     // ÷2 ×60
    Serial.printf("TACH: %d імп/с  ->  %u об/хв\n", count, rpm);
  }
}

#include "driver/gpio.h"
#include "esp_rom_sys.h"                    // esp_rom_delay_us

#define LATCH GPIO_NUM_4
#define CLK   GPIO_NUM_18
#define DATA  GPIO_NUM_23
#define S1    GPIO_NUM_32                   // кнопки: входи з підтяжкою
#define S2    GPIO_NUM_33

// байти сегментів для цифр 0..9 (спільний анод: 0 = сегмент світиться)
static const uint8_t SEG[10] = { 0xC0,0xF9,0xA4,0xB0,0x99,0x92,0x82,0xF8,0x80,0x90 };
static const uint8_t SEL[4]  = { 0xF1,0xF2,0xF4,0xF8 };   // вибір розряду 1..4

// те саме, що робить shiftOut: вісім бітів старшим уперед, такт на кожен
static void shift_out(uint8_t b) {
  for (int i = 7; i >= 0; i--) {
    gpio_set_level(DATA, (b >> i) & 1);
    gpio_set_level(CLK, 1);
    gpio_set_level(CLK, 0);
  }
}

static void show_digit(uint8_t seg, uint8_t pos) {
  gpio_set_level(LATCH, 0);
  shift_out(seg);  shift_out(SEL[pos]);     // сегменти, потім вибір розряду
  gpio_set_level(LATCH, 1);
}

static void refresh(int value) {
  int v = value < 0 ? -value : value;       // модуль для показу
  uint8_t d[4] = { (uint8_t)(v/1000%10), (uint8_t)(v/100%10),
                   (uint8_t)(v/10%10),   (uint8_t)(v%10) };
  for (uint8_t pos = 0; pos < 4; pos++) {
    show_digit(SEG[d[pos]], pos);
    esp_rom_delay_us(500);                  // трохи потримати розряд
    gpio_set_level(LATCH, 0);
    shift_out(0xFF);  shift_out(0xFF);      // погасити перед наступним
    gpio_set_level(LATCH, 1);
  }
}

void app_main(void) {
  gpio_config_t out = { .pin_bit_mask = (1ULL<<LATCH)|(1ULL<<CLK)|(1ULL<<DATA),
                        .mode = GPIO_MODE_OUTPUT };
  gpio_config(&out);
  gpio_config_t in = { .pin_bit_mask = (1ULL<<S1)|(1ULL<<S2),
                       .mode = GPIO_MODE_INPUT, .pull_up_en = GPIO_PULLUP_ENABLE };
  gpio_config(&in);

  int counter = 0;
  bool s1was = false, s2was = false;         // попередній стан для фронту
  while (1) {                                // такий цикл ще й доведеться мирити
    bool s1 = gpio_get_level(S1) == 0;       // зі сторожем задач — фон недарма
    bool s2 = gpio_get_level(S2) == 0;       // виносять у таймер
    if (s1 && !s1was) counter++;             // спрацювати раз на натиск
    if (s2 && !s2was) counter--;
    s1was = s1;  s2was = s2;
    refresh(counter);                        // перебрати розряди — раз за прохід
  }
}

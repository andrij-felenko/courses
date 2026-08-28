// Бібліотеки MFS тут немає: фон робимо самі — esp_timer + черга подій.
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

// драйвер шилда: перебір розрядів і відбивання кнопок — див. наступний розділ
void    shield_init(void);
void    shield_show(int value);
void    shield_refresh(void);       // один розряд за виклик
uint8_t shield_scan(void);          // 0 або код уже відбитої події
void    shield_beep(int ms);
void    shield_led(int n, bool on);

static QueueHandle_t events;

// те саме, що MFS робить у своєму таймерному перериванні
static void tick(void *arg) {
  shield_refresh();                       // освіжити наступний розряд
  uint8_t ev = shield_scan();             // відбити кнопки
  if (ev) xQueueSend(events, &ev, 0);     // подію — у чергу, не в обробник
}

void app_main(void) {
  int counter = 0;
  shield_init();
  events = xQueueCreate(8, sizeof(uint8_t));

  const esp_timer_create_args_t args = { .callback = tick, .name = "shield" };
  esp_timer_handle_t timer;
  ESP_ERROR_CHECK(esp_timer_create(&args, &timer));
  ESP_ERROR_CHECK(esp_timer_start_periodic(timer, 2000));   // кожні 2 мс

  shield_show(counter);                   // одразу показати початкове значення

  uint8_t ev;
  while (1) {
    if (xQueueReceive(events, &ev, portMAX_DELAY) != pdTRUE) continue;
    switch (ev) {
      case BTN1_SHORT_RELEASE: counter++; shield_beep(50);    break;  // S1 коротко: +1
      case BTN2_SHORT_RELEASE: counter--; shield_beep(50);    break;  // S2 коротко: −1
      case BTN1_LONG_PRESSED:  counter++;                     break;  // тримають: біжить угору
      case BTN2_LONG_PRESSED:  counter--;                     break;  // тримають: біжить униз
      case BTN3_LONG_RELEASE:  counter = 0; shield_beep(200); break;  // скинути в нуль
    }
    shield_show(counter);
    shield_led(1, counter < 0);           // світлодіод, поки число від'ємне
  }
}

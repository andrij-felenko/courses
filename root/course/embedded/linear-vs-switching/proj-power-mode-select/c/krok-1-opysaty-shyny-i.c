#include "driver/gpio.h"
#include "esp_sleep.h"
#include "esp_pm.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
    gpio_num_t  en_pin;        // EN перетворювача: 1 = увімкнено
    gpio_num_t  pgood_pin;     // PGOOD (вхід із підтяжкою вгору); GPIO_NUM_NC якщо немає
    uint32_t    max_rise_us;   // страховий таймаут наростання, мкс
    const char *name;
} power_rail_t;

// Порядок у масиві = порядок УВІМКНЕННЯ (згори вниз).
// Гасіння йде у ЗВОРОТНОМУ порядку (див. крок 3).
static const power_rail_t RAILS[] = {
    { BUCK5V_EN,  BUCK5V_PGOOD,  1500, "5V_main"  },  // головна шина, вмикається першою
    { BUCK12V_EN, BUCK12V_PGOOD, 3000, "12V_cam"  },  // 12 В камери/підвісу
    { LDO_SENS_EN, GPIO_NUM_NC,   500, "3V3_sens" },  // тихий LDO давачів (PGOOD нема)
};
#define RAIL_COUNT (sizeof(RAILS) / sizeof(RAILS[0]))

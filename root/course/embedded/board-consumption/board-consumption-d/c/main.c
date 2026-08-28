#include "driver/gpio.h"
#include "esp_sleep.h"

// Піни: живлення комутованої гілки й лінії давача (I2C).
#define PIN_LOAD_SWITCH   GPIO_NUM_25   // керує перемикачем живлення гілки
#define PIN_SENSOR_SDA    GPIO_NUM_21
#define PIN_SENSOR_SCL    GPIO_NUM_22
#define PIN_BATT_DIV_EN   GPIO_NUM_26   // MOSFET, що вмикає дільник виміру батареї
#define PIN_WAKE          GPIO_NUM_33   // зовнішній сигнал пробудження (переживає сон)

static void enter_deep_sleep(void)
{
    // 1) Явно приспати давач командою по шині (тут — умовний виклик драйвера),
    //    ПОКИ гілка ще під живленням, інакше команда не дійде.
    sensor_power_down();               // напр. запис у регістр CTRL режиму power-down

    // 2) Опустити сигнальні лінії до давача, щоб він не живився крізь них.
    gpio_set_level(PIN_SENSOR_SDA, 0);
    gpio_set_level(PIN_SENSOR_SCL, 0);
    gpio_set_direction(PIN_SENSOR_SDA, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_SENSOR_SCL, GPIO_MODE_OUTPUT);

    // 3) Знеструмити комутовану гілку (перемикач живлення) і вимкнути дільник батареї.
    gpio_set_level(PIN_LOAD_SWITCH, 0);   // 0 = гілка вимкнена
    gpio_set_level(PIN_BATT_DIV_EN, 0);   // дільник відрізано від землі -> не тече

    // 4) Утримати стан пінів на час сну (інакше після засинання вони «попливуть»).
    gpio_hold_en(PIN_LOAD_SWITCH);
    gpio_hold_en(PIN_BATT_DIV_EN);
    gpio_deep_sleep_hold_en();

    // 5) Джерело пробудження — зовнішній пін із завжди-живого домену
    //    (сам давач знеструмлено, будити має не він) + запасний таймер.
    esp_sleep_enable_ext0_wakeup(PIN_WAKE, 1);     // 1 = висока напруга будить
    esp_sleep_enable_timer_wakeup(60ULL * 1000000ULL);  // раз на 60 с, мкс

    // 6) У сон. Далі виконання не повернеться — вихід зі сну = перезапуск.
    esp_deep_sleep_start();
}

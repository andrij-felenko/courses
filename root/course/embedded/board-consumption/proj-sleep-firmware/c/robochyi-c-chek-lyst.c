#include "esp_sleep.h"
#include "driver/gpio.h"
#include "driver/rtc_io.h"
#include "driver/i2c.h"
#include "esp_log.h"
#include <inttypes.h>

static const char *TAG = "sleep";

// ── Карта пінів плати ─────────────────────────────────────────────────────
// Уся суть чек-листа — знати КОЖЕН пін і що з ним робити в сні.
#define PIN_SENSOR_PWR   GPIO_NUM_25   // затвор load switch гілки давача
#define PIN_I2C_SDA      GPIO_NUM_21
#define PIN_I2C_SCL      GPIO_NUM_22
#define PIN_WAKE         GPIO_NUM_33   // кнопка/переривання давача — RTC-пін!
#define PIN_STATUS_LED   GPIO_NUM_2    // лишок від DevKit, у сні гасимо

#define SENSOR_I2C_ADDR  0x76
#define SENSOR_REG_CTRL  0xF4          // регістр керування живленням давача
#define SENSOR_MODE_SLEEP 0x00         // "sleep" за даташитом давача

#define I2C_PORT         I2C_NUM_0

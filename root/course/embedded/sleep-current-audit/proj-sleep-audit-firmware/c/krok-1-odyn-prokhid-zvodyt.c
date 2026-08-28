#include "driver/gpio.h"
#include "driver/rtc_io.h"
#include "esp_sleep.h"

// Безпечний стан ніжки уві сні.
typedef enum {
    SLEEP_LOW,   // вихід, що тримає 0 В (дивиться у вузол, якому знімемо VDD)
    SLEEP_HIZ,   // вхід без підтяжок, високий опір (нічого не тягне)
} sleep_state_t;

typedef struct {
    gpio_num_t    pin;
    sleep_state_t state;
    const char   *name;   // для зрозумілих логів
} sleep_pin_t;

// Єдине джерело правди: який стан безпечний для кожної ніжки уві сні.
// Додав ніжку на платі — додав сюди рядок, і прохід її не забуде.
static const sleep_pin_t SLEEP_PROFILE[] = {
    { SENSOR_DATA_PIN, SLEEP_LOW, "sensor_data" },   // дивиться у давач → 0 В
    { SENSOR_CLK_PIN,  SLEEP_LOW, "sensor_clk"  },
    { DISPLAY_DC_PIN,  SLEEP_LOW, "display_dc"  },
    { RADIO_CS_PIN,    SLEEP_LOW, "radio_cs"    },
    { SPARE_GPIO_PIN,  SLEEP_HIZ, "spare"       },   // нікуди не штовхає → Hi-Z
};
#define SLEEP_PROFILE_LEN (sizeof(SLEEP_PROFILE) / sizeof(SLEEP_PROFILE[0]))

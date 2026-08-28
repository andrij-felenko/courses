#include "unity.h"
#include "thermostat.h"

void test_overheat_triggers_safe_mode(void) {
    Thermostat t;
    thermostat_init(&t);              // дано: свіжий стан
    thermostat_feed_temp(&t, 95);     // коли: прийшла температура 95
    TEST_ASSERT_TRUE(t.safe_mode);    // тоді: пристрій у безпечному режимі
    TEST_ASSERT_EQUAL_INT(0, t.heater_pwm);  // і нагрівач вимкнено
}

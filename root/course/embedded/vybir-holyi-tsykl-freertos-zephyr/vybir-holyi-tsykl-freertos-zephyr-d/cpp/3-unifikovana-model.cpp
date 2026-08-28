#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/sensor.h>
#include <optional>
#include <span>

namespace zephyr_app {

class LedIndicator {
public:
    explicit LedIndicator(const gpio_dt_spec& spec) : spec_(spec) {}

    bool init() {
        if (!gpio_is_ready_dt(&spec_)) {
            return false;
        }
        return gpio_pin_configure_dt(&spec_, GPIO_OUTPUT_INACTIVE) == 0;
    }

    void toggle() {
        gpio_pin_toggle_dt(&spec_);
    }

private:
    const gpio_dt_spec spec_;
};

} // namespace zephyr_app

static const struct gpio_dt_spec led_spec = GPIO_DT_SPEC_GET(DT_ALIAS(status_led), gpios);
static zephyr_app::LedIndicator s_status_led(led_spec);

extern "C" void app_cpp_main() {
    if (s_status_led.init()) {
        s_status_led.toggle();
    }
}

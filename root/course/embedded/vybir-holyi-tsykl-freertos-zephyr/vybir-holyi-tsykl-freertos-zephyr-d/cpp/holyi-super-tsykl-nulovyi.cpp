#include <cstdint>
#include <span>
#include <algorithm>

extern uint32_t get_system_ticks_ms();
extern void sensor_read_start();
extern bool sensor_is_ready();
extern void sensor_get_data(float* out_temp, float* out_press);
extern void display_update(float temp, float press);
extern void watchdog_reload();

namespace embedded {

struct TelemetryData {
    float temperature{0.0F};
    float pressure{0.0F};
};

class SuperLoopController {
public:
    void run() {
        sensor_read_start();

        while (true) {
            const uint32_t now = get_system_ticks_ms();

            poll_sensor(now);
            update_ui(now);
            watchdog_reload();
        }
    }

private:
    uint32_t last_sensor_ms_{0};
    uint32_t last_display_ms_{0};
    TelemetryData telemetry_{};

    void poll_sensor(uint32_t now) {
        if ((now - last_sensor_ms_) >= 100) {
            if (sensor_is_ready()) {
                sensor_get_data(&telemetry_.temperature, &telemetry_.pressure);
                last_sensor_ms_ = now;
                sensor_read_start();
            }
        }
    }

    void update_ui(uint32_t now) {
        if ((now - last_display_ms_) >= 500) {
            display_update(telemetry_.temperature, telemetry_.pressure);
            last_display_ms_ = now;
        }
    }
};

} // namespace embedded

void superloop_run_cpp() {
    embedded::SuperLoopController controller;
    controller.run();
}

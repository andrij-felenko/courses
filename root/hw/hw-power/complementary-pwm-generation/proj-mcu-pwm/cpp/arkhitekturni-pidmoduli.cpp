#include "driver/mcpwm_prelude.h"
#include "esp_log.h"
#include <memory>

namespace power_control {

class Esp32HalfBridgePwm {
public:
    struct Pins {
        int high_side_gpio;
        int low_side_gpio;
    };

    Esp32HalfBridgePwm(Pins pins, uint32_t pwm_freq_hz, uint32_t dead_time_ns)
        : pins_(pins), freq_hz_(pwm_freq_hz), dead_time_ns_(dead_time_ns) {}

    ~Esp32HalfBridgePwm() {
        if (timer_) {
            mcpwm_timer_start_stop(timer_, MCPWM_TIMER_STOP_EMPTY);
            mcpwm_timer_disable(timer_);
            mcpwm_del_timer(timer_);
        }
        if (oper_) mcpwm_del_operator(oper_);
    }

    void start() {
        mcpwm_timer_config_t timer_cfg = {
            .group_id = 0,
            .clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT,
            .resolution_hz = 10'000'000,
            .period_ticks = static_cast<uint32_t>(10'000'000 / (2 * freq_hz_)),
            .count_mode = MCPWM_TIMER_COUNT_MODE_UP_DOWN,
        };
        ESP_ERROR_CHECK(mcpwm_new_timer(&timer_cfg, &timer_));

        mcpwm_operator_config_t oper_cfg = {.group_id = 0};
        ESP_ERROR_CHECK(mcpwm_new_operator(&oper_cfg, &oper_));
        ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper_, timer_));

        mcpwm_comparator_config_t cmpr_cfg = {.flags = {.update_cmp_on_tez = true}};
        ESP_ERROR_CHECK(mcpwm_new_comparator(oper_, &cmpr_cfg, &cmpr_));

        mcpwm_generator_config_t gh_cfg = {.gen_gpio_num = pins_.high_side_gpio};
        ESP_ERROR_CHECK(mcpwm_new_generator(oper_, &gh_cfg, &gen_high_));

        mcpwm_generator_config_t gl_cfg = {.gen_gpio_num = pins_.low_side_gpio};
        ESP_ERROR_CHECK(mcpwm_new_generator(oper_, &gl_cfg, &gen_low_));

        // Конфігурація подій та мертвого часу
        ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(
            gen_high_,
            MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, MCPWM_TIMER_EVENT_EMPTY, MCPWM_GEN_ACTION_HIGH)));
        ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(
            gen_high_,
            MCPWM_GEN_COMPARE_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP, cmpr_, MCPWM_GEN_ACTION_LOW)));

        mcpwm_dead_time_config_t dt_cfg = {
            .posedge_path = MCPWM_DEAD_TIME_PATH_ACTIVE,
            .negedge_path = MCPWM_DEAD_TIME_PATH_INVERT,
        };
        ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high_, gen_high_, &dt_cfg));
        ESP_ERROR_CHECK(mcpwm_generator_set_dead_time(gen_high_, gen_low_, &dt_cfg));

        ESP_ERROR_CHECK(mcpwm_timer_enable(timer_));
        ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer_, MCPWM_TIMER_START_NO_STOP));
    }

private:
    Pins pins_;
    uint32_t freq_hz_;
    uint32_t dead_time_ns_;
    mcpwm_timer_handle_t timer_{nullptr};
    mcpwm_oper_handle_t oper_{nullptr};
    mcpwm_cmpr_handle_t cmpr_{nullptr};
    mcpwm_gen_handle_t gen_high_{nullptr};
    mcpwm_gen_handle_t gen_low_{nullptr};
};

} // namespace power_control

#include "driver/ledc.h"
#include "esp_err.h"
#include <algorithm>

class Esp32SymmetricServo {
private:
    gpio_num_t gpioPin;
    ledc_channel_t channel;
    int neutralUs;
    int deadbandUs;
    int minRevUs;
    int maxFwdUs;

    uint32_t usToDuty(uint32_t us) const {
        return (us * ((1 << 14) - 1)) / 20000;
    }

public:
    Esp32SymmetricServo(gpio_num_t pin, ledc_channel_t ch, int neutral = 1500, int deadband = 8, int minRev = 1050, int maxFwd = 1950)
        : gpioPin(pin), channel(ch), neutralUs(neutral), deadbandUs(deadband), minRevUs(minRev), maxFwdUs(maxFwd) {}

    esp_err_t init() {
        ledc_timer_config_t timerConf = {
            .speed_mode = LEDC_LOW_SPEED_MODE,
            .duty_resolution = LEDC_TIMER_14_BIT,
            .timer_num = LEDC_TIMER_0,
            .freq_hz = 50,
            .clk_cfg = LEDC_AUTO_CLK
        };
        esp_err_t err = ledc_timer_config(&timerConf);
        if (err != ESP_OK) return err;

        ledc_channel_config_t channelConf = {
            .gpio_num = gpioPin,
            .speed_mode = LEDC_LOW_SPEED_MODE,
            .channel = channel,
            .intr_type = LEDC_INTR_DISABLE,
            .timer_sel = LEDC_TIMER_0,
            .duty = 0,
            .hpoint = 0
        };
        return ledc_channel_config(&channelConf);
    }

    void setSpeedNormalized(float speedNorm) {
        speedNorm = std::clamp(speedNorm, -1.0f, 1.0f);
        int outputUs = neutralUs;

        if (speedNorm > 0.001f) {
            int activeStart = neutralUs + deadbandUs;
            outputUs = activeStart + static_cast<int>(speedNorm * (maxFwdUs - activeStart));
        } else if (speedNorm < -0.001f) {
            int activeStart = neutralUs - deadbandUs;
            outputUs = activeStart + static_cast<int>(speedNorm * (activeStart - minRevUs));
        } else {
            outputUs = neutralUs;
        }

        uint32_t duty = usToDuty(outputUs);
        ledc_set_duty(LEDC_LOW_SPEED_MODE, channel, duty);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, channel);
    }
};

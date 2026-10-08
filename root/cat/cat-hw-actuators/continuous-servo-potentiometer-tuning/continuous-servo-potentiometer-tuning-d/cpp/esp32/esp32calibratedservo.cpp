#include "driver/ledc.h"
#include "esp_err.h"
#include <cmath>

class Esp32CalibratedServo {
private:
    gpio_num_t gpioPin;
    ledc_channel_t channel;
    ledc_timer_t timer;
    int neutralOffsetUs;
    int deadbandUs;

    uint32_t usToDuty(uint32_t us) const {
        return (us * ((1 << 14) - 1)) / 20000;
    }

public:
    Esp32CalibratedServo(gpio_num_t pin, ledc_channel_t ch, int offsetUs = 0, int deadbandUsWidth = 10)
        : gpioPin(pin), channel(ch), timer(LEDC_TIMER_0),
          neutralOffsetUs(offsetUs), deadbandUs(deadbandUsWidth) {}

    esp_err_t init() {
        ledc_timer_config_t timerConf = {
            .speed_mode = LEDC_LOW_SPEED_MODE,
            .duty_resolution = LEDC_TIMER_14_BIT,
            .timer_num = timer,
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
            .timer_sel = timer,
            .duty = 0,
            .hpoint = 0
        };
        return ledc_channel_config(&channelConf);
    }

    void writeMicrosecondsCalibrated(int targetPulseUs) {
        int effectiveNeutral = 1500 + neutralOffsetUs;
        int delta = targetPulseUs - 1500;
        int outputPulseUs;

        if (std::abs(delta) <= deadbandUs) {
            outputPulseUs = effectiveNeutral;
        } else {
            outputPulseUs = targetPulseUs + neutralOffsetUs;
        }

        uint32_t duty = usToDuty(outputPulseUs);
        ledc_set_duty(LEDC_LOW_SPEED_MODE, channel, duty);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, channel);
    }
};

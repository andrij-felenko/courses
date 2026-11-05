#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"
#include "soc/gpio_struct.h"
#include <stdint.h>

// Клас високошвидкісного Bit-bang драйвера для платформи ESP32 (ESP-IDF)
class Esp32BitBangSpi {
public:
    Esp32BitBangSpi(gpio_num_t sck, gpio_num_t mosi, gpio_num_t miso)
        : sck_mask_(1ULL << sck), mosi_mask_(1ULL << mosi), miso_num_(miso) {
        
        gpio_config_t io_conf = {};
        io_conf.mode = GPIO_MODE_OUTPUT;
        io_conf.pin_bit_mask = sck_mask_ | mosi_mask_;
        gpio_config(&io_conf);

        io_conf.mode = GPIO_MODE_INPUT;
        io_conf.pin_bit_mask = (1ULL << miso);
        gpio_config(&io_conf);

        vPortCPUInitializeMutex(&mux_);
    }

    uint8_t IRAM_ATTR transfer(uint8_t tx_data) {
        uint8_t rx_data = 0;

        // Використання спінлоку ESP-IDF для захисту від контекстних переключень
        portENTER_CRITICAL(&mux_);

        for (int i = 7; i >= 0; i--) {
            if (tx_data & (1U << i)) {
                GPIO.out_w1ts = mosi_mask_; // Встановлення логічної одиниці
            } else {
                GPIO.out_w1tc = mosi_mask_; // Скидання в логічний нуль
            }

            GPIO.out_w1ts = sck_mask_;      // Строб годинника high

            if (GPIO.in & (1U << miso_num_)) {
                rx_data |= (1U << i);
            }

            GPIO.out_w1tc = sck_mask_;      // Строб годинника low
        }

        portEXIT_CRITICAL(&mux_);
        return rx_data;
    }

private:
    uint32_t sck_mask_;
    uint32_t mosi_mask_;
    gpio_num_t miso_num_;
    portMUX_TYPE mux_ = portMUX_INITIALIZER_UNLOCKED;
};

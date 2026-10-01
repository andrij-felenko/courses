#pragma once

#include <cstdint>
#include <array>
#include <span>
#include "driver/gpio.h"
#include "driver/rmt_tx.h"
#include "esp_err.h"

namespace esp32_zero {

// Структура кольору в форматі RGB
struct Color {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};

    static constexpr Color Red() noexcept { return {255, 0, 0}; }
    static constexpr Color Green() noexcept { return {0, 255, 0}; }
    static constexpr Color Blue() noexcept { return {0, 0, 255}; }
    static constexpr Color Yellow() noexcept { return {255, 200, 0}; }
    static constexpr Color Purple() noexcept { return {180, 0, 255}; }
    static constexpr Color Off() noexcept { return {0, 0, 0}; }
};

// Перерахування системних статусів пристрою
enum class DongleStatus : uint8_t {
    Initializing,
    WifiConnecting,
    WifiConnected,
    DataTransferring,
    Error
};

// Асинхронний контролер адресного RGB-світлодіода (WS2812/SK6812) на платі ESP32-S3-Zero
class RmtLedController {
public:
    explicit RmtLedController(gpio_num_t gpio_pin = GPIO_NUM_21) noexcept
        : gpio_pin_(gpio_pin) {}

    ~RmtLedController() {
        deinit();
    }

    // Заборона копіювання для запобігання дублюванню RMT каналу
    RmtLedController(const RmtLedController&) = delete;
    RmtLedController& operator=(const RmtLedController&) = delete;

    RmtLedController(RmtLedController&& other) noexcept
        : gpio_pin_(other.gpio_pin_),
          rmt_channel_(other.rmt_channel_),
          rmt_encoder_(other.rmt_encoder_),
          current_status_(other.current_status_),
          current_color_(other.current_color_),
          last_update_ms_(other.last_update_ms_),
          blink_state_(other.blink_state_) {
        other.rmt_channel_ = nullptr;
        other.rmt_encoder_ = nullptr;
    }

    RmtLedController& operator=(RmtLedController&& other) noexcept {
        if (this != &other) {
            deinit();
            gpio_pin_ = other.gpio_pin_;
            rmt_channel_ = other.rmt_channel_;
            rmt_encoder_ = other.rmt_encoder_;
            current_status_ = other.current_status_;
            current_color_ = other.current_color_;
            last_update_ms_ = other.last_update_ms_;
            blink_state_ = other.blink_state_;
            other.rmt_channel_ = nullptr;
            other.rmt_encoder_ = nullptr;
        }
        return *this;
    }

    // Налаштування та запуск RMT TX каналу
    bool begin() {
        rmt_tx_channel_config_t tx_chan_config = {
            .gpio_num = gpio_pin_,
            .clk_src = RMT_CLK_SRC_DEFAULT,
            .resolution_hz = 10'000'000, // 10 МГц (1 тика = 100 нс)
            .mem_block_symbols = 64,
            .trans_queue_depth = 4,
            .flags = {
                .invert_out = false,
                .with_dma = false,
            }
        };

        if (rmt_new_tx_channel(&tx_chan_config, &rmt_channel_) != ESP_OK) {
            return false;
        }

        rmt_copy_encoder_config_t copy_encoder_config = {};
        if (rmt_new_copy_encoder(&copy_encoder_config, &rmt_encoder_) != ESP_OK) {
            rmt_del_channel(rmt_channel_);
            rmt_channel_ = nullptr;
            return false;
        }

        if (rmt_enable(rmt_channel_) != ESP_OK) {
            rmt_del_encoder(rmt_encoder_);
            rmt_del_channel(rmt_channel_);
            rmt_channel_ = nullptr;
            rmt_encoder_ = nullptr;
            return false;
        }

        setStatus(DongleStatus::Initializing);
        return true;
    }

    // Встановлення точного кольору світлодіода
    void setPixel(Color color) {
        current_color_ = color;
        transmitColor(color);
    }

    // Встановлення системного стану пристрою
    void setStatus(DongleStatus status) {
        current_status_ = status;
        switch (status) {
            case DongleStatus::Initializing:
                setPixel(Color::Yellow());
                break;
            case DongleStatus::WifiConnecting:
                setPixel(Color::Purple());
                break;
            case DongleStatus::WifiConnected:
                setPixel(Color::Green());
                break;
            case DongleStatus::DataTransferring:
                setPixel(Color::Blue());
                break;
            case DongleStatus::Error:
                setPixel(Color::Red());
                break;
        }
    }

    // Асинхронне фонове оновлення ефектів індикації (блимання)
    void update(uint32_t now_ms) {
        if (current_status_ == DongleStatus::WifiConnecting) {
            if (now_ms - last_update_ms_ >= 300) {
                last_update_ms_ = now_ms;
                blink_state_ = !blink_state_;
                transmitColor(blink_state_ ? Color::Purple() : Color::Off());
            }
        } else if (current_status_ == DongleStatus::DataTransferring) {
            if (now_ms - last_update_ms_ >= 100) {
                last_update_ms_ = now_ms;
                blink_state_ = !blink_state_;
                transmitColor(blink_state_ ? Color::Blue() : Color::Green());
            }
        }
    }

    [[nodiscard]] DongleStatus getStatus() const noexcept {
        return current_status_;
    }

private:
    void transmitColor(Color color) {
        if (!rmt_channel_ || !rmt_encoder_) return;

        // Генерація символів RMT для протоколу WS2812 (порядок GRB)
        static constexpr rmt_symbol_word_t bit0 = {{{ 4, 1, 9, 0 }}}; // 400ns high, 900ns low
        static constexpr rmt_symbol_word_t bit1 = {{{ 9, 1, 4, 0 }}}; // 900ns high, 400ns low

        std::array<rmt_symbol_word_t, 24> symbols{};
        uint32_t grb = (static_cast<uint32_t>(color.g) << 16) |
                       (static_cast<uint32_t>(color.r) << 8)  |
                        static_cast<uint32_t>(color.b);

        for (int i = 0; i < 24; ++i) {
            symbols[i] = (grb & (1 << (23 - i))) ? bit1 : bit0;
        }

        rmt_transmit_config_t tx_config = {
            .loop_count = 0,
        };

        rmt_transmit(rmt_channel_, rmt_encoder_, symbols.data(), sizeof(symbols), &tx_config);
    }

    void deinit() {
        if (rmt_channel_) {
            rmt_disable(rmt_channel_);
            if (rmt_encoder_) {
                rmt_del_encoder(rmt_encoder_);
                rmt_encoder_ = nullptr;
            }
            rmt_del_channel(rmt_channel_);
            rmt_channel_ = nullptr;
        }
    }

    gpio_num_t gpio_pin_{GPIO_NUM_21};
    rmt_channel_handle_t rmt_channel_{nullptr};
    rmt_encoder_handle_t rmt_encoder_{nullptr};
    DongleStatus current_status_{DongleStatus::Initializing};
    Color current_color_{Color::Off()};
    uint32_t last_update_ms_{0};
    bool blink_state_{false};
};

} // namespace esp32_zero

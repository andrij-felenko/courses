#pragma once

// Тіла задач як об'єкти: стан задачі — поля, а не статичні змінні файлу.
// Кожен run() пишеться лінійно й має право блокуватися.
#include "board.hpp"
#include "message_queue.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>

namespace app {

struct Sample {
    std::uint32_t stamp_ms{0};
    std::int32_t centi_celsius{0};
    std::uint16_t seq{0};
    std::uint16_t errors{0};
};

using SampleQueue = rtos::StaticQueue<Sample, 4>;

inline constexpr std::uint32_t kAliveSensor = 1U << 0;
inline constexpr std::uint32_t kAliveDisplay = 1U << 1;
inline constexpr std::uint32_t kAliveAll = kAliveSensor | kAliveDisplay;

class SensorWorker {
public:
    SensorWorker(SampleQueue &queue, TaskHandle_t supervisor) noexcept
        : queue_{queue}, supervisor_{supervisor} {}

    void run()
    {
        TickType_t wake = xTaskGetTickCount();
        bool ready = begin().has_value();

        for (;;) {
            if (!ready) {
                ready = begin().has_value(); // датчик міг пізніше отримати живлення
            } else if (auto value = measure()) {
                sample_.stamp_ms = static_cast<std::uint32_t>(xTaskGetTickCount() * portTICK_PERIOD_MS);
                sample_.centi_celsius = *value;
                ++sample_.seq;
                queue_.send_newest(sample_);
            } else {
                ++sample_.errors;
                ready = false;
            }

            xTaskNotify(supervisor_, kAliveSensor, eSetBits);
            // Період від попереднього пробудження: дрейф не накопичується.
            xTaskDelayUntil(&wake, pdMS_TO_TICKS(100));
        }
    }

private:
    std::expected<void, board::BusError> begin() noexcept
    {
        std::array<std::uint8_t, 1> id{};
        std::array<std::uint8_t, 6> calib{};

        if (auto r = bus_.read_regs(0xD0U, id); !r) { return r; }
        if (id[0] != 0x60U) { return std::unexpected{board::BusError::Nack}; }
        if (auto r = bus_.read_regs(0x88U, calib); !r) { return r; }

        t1_ = static_cast<std::uint16_t>(calib[1] << 8 | calib[0]);
        t2_ = static_cast<std::int16_t>(calib[3] << 8 | calib[2]);
        t3_ = static_cast<std::int16_t>(calib[5] << 8 | calib[4]);
        return {};
    }

    std::optional<std::int32_t> measure() noexcept
    {
        std::array<std::uint8_t, 3> raw{};

        if (!bus_.write_reg(0xF4U, 0x21U)) { // forced, oversampling x1
            return std::nullopt;
        }
        // П'ять мілісекунд перетворення віддаємо іншим задачам — у голому
        // циклі цей час довелося б розрізати на стани автомата.
        vTaskDelay(pdMS_TO_TICKS(5));

        if (!bus_.read_regs(0xFAU, raw)) { return std::nullopt; }

        const std::int32_t adc = (std::int32_t{raw[0]} << 12) | (std::int32_t{raw[1]} << 4) |
                                 (std::int32_t{raw[2]} >> 4);
        if (adc == 0x80000) { return std::nullopt; }

        const std::int32_t var1 = (((adc >> 3) - (std::int32_t{t1_} << 1)) * std::int32_t{t2_}) >> 11;
        const std::int32_t d = (adc >> 4) - std::int32_t{t1_};
        const std::int32_t var2 = (((d * d) >> 12) * std::int32_t{t3_}) >> 14;
        return ((var1 + var2) * 5 + 128) >> 8;
    }

    board::I2cBus bus_{0x76};
    SampleQueue &queue_;
    TaskHandle_t supervisor_;
    Sample sample_{};
    std::uint16_t t1_{0};
    std::int16_t t2_{0};
    std::int16_t t3_{0};
};

class DisplayWorker {
public:
    DisplayWorker(SampleQueue &queue, TaskHandle_t supervisor) noexcept
        : queue_{queue}, supervisor_{supervisor} {}

    void run()
    {
        bool ready = begin().has_value();

        for (;;) {
            // Поки даних немає, задача не з'їдає жодного такту процесора.
            if (auto sample = queue_.receive(pdMS_TO_TICKS(500))) {
                if (!ready) {
                    ready = begin().has_value();
                }
                if (ready) {
                    draw_bar(3, sample->centi_celsius, -1000, 5000);
                    // Кадр висить на шині ≈33 мс, і весь цей час задача
                    // датчика спокійно витісняє екран — у неї вищий пріоритет.
                    ready = flush().has_value();
                }
            }
            xTaskNotify(supervisor_, kAliveDisplay, eSetBits);
        }
    }

private:
    std::expected<void, board::BusError> begin() noexcept
    {
        static constexpr std::array<std::uint8_t, 25> kInit{
            0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0x8D, 0x14,
            0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12, 0x81, 0x7F, 0xD9, 0xF1,
            0xDB, 0x40, 0xA4, 0xA6, 0xAF};

        board::SpiBus::reset_pin(false);
        vTaskDelay(pdMS_TO_TICKS(2));
        board::SpiBus::reset_pin(true);
        vTaskDelay(pdMS_TO_TICKS(2));

        for (std::uint8_t c : kInit) {
            if (auto r = command(c); !r) { return r; }
        }
        return {};
    }

    static std::expected<void, board::BusError> command(std::uint8_t c) noexcept
    {
        board::SpiBus::data_mode(false);
        board::SpiBus::select(true);
        auto r = board::SpiBus::write(std::span{&c, 1});
        board::SpiBus::select(false);
        return r;
    }

    void draw_bar(std::size_t page, std::int32_t value, std::int32_t lo, std::int32_t hi) noexcept
    {
        const std::int32_t span = hi - lo;
        if (span <= 0) { return; }
        value = std::clamp(value, lo, hi);

        const std::int32_t width = (value - lo) * 128 / span;
        auto row = std::span{fb_}.subspan(page * 128, 128);
        for (std::size_t x = 0; x < row.size(); ++x) {
            row[x] = (static_cast<std::int32_t>(x) < width) ? 0x3CU : 0x00U;
        }
    }

    std::expected<void, board::BusError> flush() noexcept
    {
        static constexpr std::array<std::uint8_t, 6> kWindow{0x21, 0x00, 0x7F, 0x22, 0x00, 0x07};

        for (std::uint8_t c : kWindow) {
            if (auto r = command(c); !r) { return r; }
        }
        board::SpiBus::data_mode(true);
        board::SpiBus::select(true);
        auto r = board::SpiBus::write(fb_);
        board::SpiBus::select(false);
        return r;
    }

    SampleQueue &queue_;
    TaskHandle_t supervisor_;
    std::array<std::uint8_t, 128 * 8> fb_{};
};

// Супервізор гладить watchdog лише тоді, коли обидві робочі задачі відзвітували,
// і сам стежить за недоторканим запасом їхніх стеків.
class Supervisor {
public:
    using StackProbe = std::size_t (*)();

    Supervisor(StackProbe sensor_free, StackProbe display_free) noexcept
        : sensor_free_{sensor_free}, display_free_{display_free} {}

    void run()
    {
        constexpr std::size_t kLowWaterBytes = 128;
        std::uint32_t alive = 0U;

        for (;;) {
            std::uint32_t bits = 0U;
            if (xTaskNotifyWait(0U, 0xFFFFFFFFU, &bits, pdMS_TO_TICKS(250)) == pdTRUE) {
                alive |= bits;
            }

            if ((alive & kAliveAll) == kAliveAll) {
                alive = 0U;
                board::kick_watchdog();
            }

            if ((sensor_free_() < kLowWaterBytes) || (display_free_() < kLowWaterBytes)) {
                configASSERT(0); // стек на межі — краще впасти на столі
            }
        }
    }

private:
    StackProbe sensor_free_;
    StackProbe display_free_;
};

} // namespace app

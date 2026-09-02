/* Програмний ведучий I2C поверх двох ліній з відкритим стоком.
   Володіння виводами тримає сам об'єкт: конструктор забирає їх у GPIO,
   деструктор повертає апаратному блоку — хай навіть вихід стався винятком. */
#pragma once

#include <cstdint>
#include <expected>

#include "bus_lines.hpp"

template <OpenDrainLines Lines>
class BitBangMaster {
public:
    struct IdleState {
        bool scl_high;
        bool sda_high;
    };

    explicit BitBangMaster(Lines& lines) : lines_{lines} { lines_.take_pins(); }
    ~BitBangMaster() { lines_.give_pins_back(); }

    BitBangMaster(const BitBangMaster&) = delete;
    BitBangMaster& operator=(const BitBangMaster&) = delete;

    /* Рівні обох ліній у спокої: справна шина дає 1 і 1 */
    [[nodiscard]] IdleState idle_state() {
        lines_.scl_release();
        lines_.sda_release();
        lines_.delay_us(half_period_us);
        return IdleState{lines_.scl_read(), lines_.sda_read()};
    }

    /* Дев'ять тактів SCL і примусовий STOP; false — лінію так і не віддали */
    [[nodiscard]] bool recover_bus() {
        if (lines_.sda_read()) {
            return true; /* шина вільна, виштовхувати нічого */
        }

        lines_.sda_release();
        lines_.scl_release();
        lines_.delay_us(half_period_us);

        bool released = false;
        for (int i = 0; i < 9 && !released; ++i) {
            lines_.scl_drive_low();
            lines_.delay_us(half_period_us);
            lines_.scl_release();
            lines_.delay_us(half_period_us);
            released = lines_.sda_read();
        }
        if (!released) {
            return false; /* це вже не зависання, а замикання SDA на землю */
        }

        /* Примусовий STOP повертає веденого у вихідний стан */
        lines_.sda_drive_low();
        lines_.delay_us(half_period_us);
        lines_.scl_release();
        lines_.delay_us(half_period_us);
        lines_.sda_release();
        lines_.delay_us(half_period_us);
        return lines_.sda_read();
    }

    /* Транзакція нульової довжини: START, адресний байт запису, ACK, STOP */
    [[nodiscard]] std::expected<void, BusError> probe(std::uint8_t addr7) {
        if (auto started = start(); !started) {
            return started;
        }

        /* STOP мусить піти навіть тоді, коли байт обірвався помилкою */
        StopOnExit stopper{*this};

        const auto frame = static_cast<std::uint8_t>(addr7 << 1); /* молодший біт 0 — запис */
        for (int bit = 7; bit >= 0; --bit) {
            if (auto written = write_bit(((frame >> bit) & 1U) != 0U); !written) {
                return written;
            }
        }

        const auto ack = read_ack();
        if (!ack) {
            return std::unexpected{ack.error()};
        }

        stopper.armed = false;
        if (auto stopped = stop(); !stopped) {
            return stopped;
        }
        if (!*ack) {
            return std::unexpected{BusError::nack};
        }
        return {};
    }

private:
    /* Півперіод 5 мкс — це приблизно 100 кГц, стандартна швидкість шини */
    static constexpr std::uint32_t half_period_us = 5;
    /* Скільки терпимо розтягнутий веденим такт, поки не визнаємо лінію мертвою */
    static constexpr std::uint32_t stretch_timeout_us = 2000;

    struct StopOnExit {
        BitBangMaster& master;
        bool armed = true;
        ~StopOnExit() {
            if (armed) {
                (void)master.stop();
            }
        }
    };

    /* Ведений має право притримати такт; ненормально — тримати його вічно */
    [[nodiscard]] std::expected<void, BusError> release_scl_and_wait() {
        lines_.scl_release();
        for (std::uint32_t waited = 0; !lines_.scl_read(); waited += 1) {
            if (waited >= stretch_timeout_us) {
                return std::unexpected{BusError::stretch_timeout};
            }
            lines_.delay_us(1);
        }
        lines_.delay_us(half_period_us);
        return {};
    }

    /* START: перепад SDA з 1 у 0 при високому SCL */
    [[nodiscard]] std::expected<void, BusError> start() {
        lines_.sda_release();
        if (auto high = release_scl_and_wait(); !high) {
            return high;
        }
        if (!lines_.sda_read()) {
            return std::unexpected{BusError::lines_busy};
        }

        lines_.sda_drive_low();
        lines_.delay_us(half_period_us);
        lines_.scl_drive_low();
        lines_.delay_us(half_period_us);
        return {};
    }

    /* STOP: перепад SDA з 0 у 1 при високому SCL */
    [[nodiscard]] std::expected<void, BusError> stop() {
        lines_.sda_drive_low();
        lines_.delay_us(half_period_us);
        if (auto high = release_scl_and_wait(); !high) {
            return high;
        }
        lines_.sda_release();
        lines_.delay_us(half_period_us);
        if (!lines_.sda_read()) {
            return std::unexpected{BusError::stop_failed};
        }
        return {};
    }

    /* Біт виставляється при низькому SCL, читається на висхідному фронті */
    [[nodiscard]] std::expected<void, BusError> write_bit(bool bit) {
        if (bit) {
            lines_.sda_release();
        } else {
            lines_.sda_drive_low();
        }
        lines_.delay_us(half_period_us);

        if (auto high = release_scl_and_wait(); !high) {
            return high;
        }
        lines_.scl_drive_low();
        lines_.delay_us(half_period_us);
        return {};
    }

    /* Дев'ятий такт: ведучий відпускає SDA, ведений притягує її на знак ACK */
    [[nodiscard]] std::expected<bool, BusError> read_ack() {
        lines_.sda_release();
        lines_.delay_us(half_period_us);

        if (auto high = release_scl_and_wait(); !high) {
            return std::unexpected{high.error()};
        }
        const bool ack = !lines_.sda_read();
        lines_.scl_drive_low();
        lines_.delay_us(half_period_us);
        return ack;
    }

    Lines& lines_;
};

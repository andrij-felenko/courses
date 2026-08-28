// RS485Driver.hpp — Ідіоматичний об'єктно-орієнтований драйвер RS-485 на C++20
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <concepts>

enum class DriverState : uint8_t {
    Idle,
    Receiving,
    Transmitting,
    FrameReady
};

template <typename HardwareInterface, size_t BufferCapacity = 256>
class RS485Port {
public:
    explicit RS485Port(HardwareInterface& hw) : hw_{hw} {
        hw_.set_driver_enable(false);
    }

    bool send(std::span<const uint8_t> data) {
        if (data.empty() || data.size() > BufferCapacity || state_ == DriverState::Transmitting) {
            return false;
        }

        for (size_t i = 0; i < data.size(); ++i) {
            tx_buffer_[i] = data[i];
        }
        tx_length_ = data.size();
        tx_index_ = 0;
        state_ = DriverState::Transmitting;

        // Вмикаємо DE перед передачею першого байта
        hw_.set_driver_enable(true);
        hw_.write_byte(tx_buffer_[tx_index_++]);
        return true;
    }

    void on_uart_txe_interrupt() {
        if (state_ != DriverState::Transmitting) return;

        if (tx_index_ < tx_length_) {
            hw_.write_byte(tx_buffer_[tx_index_++]);
        } else {
            hw_.enable_tc_interrupt(true);
        }
    }

    void on_uart_tc_interrupt() {
        if (state_ == DriverState::Transmitting) {
            hw_.enable_tc_interrupt(false);
            // Вимикаємо передавач строго після фізичного завершення стоп-біта
            hw_.set_driver_enable(false);
            state_ = DriverState::Idle;
        }
    }

    void on_uart_rxne_interrupt(uint8_t byte) {
        if (state_ == DriverState::Transmitting) return;

        if (rx_count_ < BufferCapacity) {
            rx_buffer_[rx_count_++] = byte;
            state_ = DriverState::Receiving;
        }
    }

    void on_bus_idle_timeout() {
        if (state_ == DriverState::Receiving && rx_count_ > 0) {
            state_ = DriverState::FrameReady;
        }
    }

    [[nodiscard]] std::optional<std::span<const uint8_t>> get_received_frame() {
        if (state_ != DriverState::FrameReady) {
            return std::nullopt;
        }
        return std::span<const uint8_t>{rx_buffer_.data(), rx_count_};
    }

    void release_rx_buffer() {
        rx_count_ = 0;
        state_ = DriverState::Idle;
    }

    [[nodiscard]] DriverState state() const noexcept { return state_; }

private:
    HardwareInterface& hw_;
    std::array<uint8_t, BufferCapacity> tx_buffer_{};
    std::array<uint8_t, BufferCapacity> rx_buffer_{};
    size_t tx_length_{0};
    size_t tx_index_{0};
    size_t rx_count_{0};
    DriverState state_{DriverState::Idle};
};

#pragma once

// Шина SPI для одного підпорядкованого пристрою. Уся суть класу —
// у вкладеному Select: лінія CS притискається на вході в область
// видимості й відпускається на виході з неї, хоч би як ми звідти вийшли.

#include <array>
#include <cstdint>
#include <expected>
#include <span>

#include "stm32g0xx_hal.h"

namespace rtd {

enum class BusError {
    TransferFailed,  // обмін не відбувся
    FrameTooLong     // кадр не вміщається у внутрішній буфер
};

class SpiDevice {
public:
    SpiDevice(SPI_HandleTypeDef& spi, GPIO_TypeDef* csPort, std::uint16_t csPin) noexcept
        : spi_{&spi}, csPort_{csPort}, csPin_{csPin} {
        // У спокої CS високий, інакше мікросхема з'їсть перший же байт
        HAL_GPIO_WritePin(csPort_, csPin_, GPIO_PIN_SET);
    }

    // ADS1220 відповідає на кожен переданий байт, тож читання й запис —
    // це один і той самий обмін. Порожній rx означає «відповідь не потрібна».
    [[nodiscard]] std::expected<void, BusError> transfer(std::span<const std::uint8_t> tx,
                                                         std::span<std::uint8_t> rx) noexcept {
        std::array<std::uint8_t, kMaxFrame> scratch{};
        if (tx.size() > scratch.size()) {
            return std::unexpected(BusError::FrameTooLong);
        }
        if (!rx.empty() && rx.size() < tx.size()) {
            return std::unexpected(BusError::FrameTooLong);
        }

        std::uint8_t* destination = rx.empty() ? scratch.data() : rx.data();

        const Select selected{*this};
        const HAL_StatusTypeDef status =
            HAL_SPI_TransmitReceive(spi_,
                                    const_cast<std::uint8_t*>(tx.data()),
                                    destination,
                                    static_cast<std::uint16_t>(tx.size()),
                                    kTimeoutMs);
        if (status != HAL_OK) {
            return std::unexpected(BusError::TransferFailed);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, BusError> write(std::span<const std::uint8_t> tx) noexcept {
        return transfer(tx, {});
    }

private:
    static constexpr std::size_t   kMaxFrame  = 8;
    static constexpr std::uint32_t kTimeoutMs = 10;

    class Select {
    public:
        explicit Select(SpiDevice& device) noexcept : device_{device} {
            HAL_GPIO_WritePin(device_.csPort_, device_.csPin_, GPIO_PIN_RESET);
        }
        ~Select() { HAL_GPIO_WritePin(device_.csPort_, device_.csPin_, GPIO_PIN_SET); }

        Select(const Select&) = delete;
        Select& operator=(const Select&) = delete;

    private:
        SpiDevice& device_;
    };

    SPI_HandleTypeDef* spi_;
    GPIO_TypeDef*      csPort_;
    std::uint16_t      csPin_;
};

}  // namespace rtd

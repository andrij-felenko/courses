#pragma once

#include "hal.hpp"

namespace board {

/* Дешифратор 74HC138 як генератор ліній Chip Select.
   a3 == kNoPin — один чип, 8 ліній. Інакше два каскадовані: старший біт іде
   на прямий вхід дозволу першого й на інверсний другого, а спільний строб
   enable — на інверсний вхід дозволу обох. Виходить 16 ліній CS ціною
   п'яти виводів мікроконтролера. */
class Hc138ChipSelect {
public:
    struct Pins {
        std::uint8_t a0{};
        std::uint8_t a1{};
        std::uint8_t a2{};
        std::uint8_t a3{kNoPin};
        std::uint8_t enable{};
    };

    Hc138ChipSelect(GpioPort& gpio, const Pins& pins);

    /* Вибраний чип живе, доки живе цей об'єкт. Деструктор знімає дозвіл. */
    class Selection {
    public:
        Selection(Selection&& other) noexcept;
        Selection(const Selection&) = delete;
        Selection& operator=(const Selection&) = delete;
        Selection& operator=(Selection&&) = delete;
        ~Selection();

        [[nodiscard]] std::uint8_t device() const noexcept { return device_; }

    private:
        friend class Hc138ChipSelect;
        Selection(Hc138ChipSelect& owner, std::uint8_t device) noexcept
            : owner_(&owner), device_(device) {}

        Hc138ChipSelect* owner_;
        std::uint8_t device_;
    };

    [[nodiscard]] Result<Selection> select(std::uint8_t device);

    /* Команда й дані в одній сесії CS. */
    Result<void> command(SpiBus& spi, std::uint8_t device,
                         std::span<const std::uint8_t> cmd,
                         std::span<const std::uint8_t> tx,
                         std::span<std::uint8_t> rx);

    [[nodiscard]] std::uint8_t lines() const noexcept {
        return pins_.a3 == kNoPin ? 8 : 16;
    }

private:
    void release() noexcept;

    GpioPort& gpio_;
    Pins pins_;
};

}  // namespace board

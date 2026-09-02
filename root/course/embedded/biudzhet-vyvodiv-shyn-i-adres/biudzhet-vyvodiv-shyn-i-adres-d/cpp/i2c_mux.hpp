#pragma once

#include "hal.hpp"

namespace board {

/* Восьмиканальний комутатор шини TCA9548A. */
class Tca9548a {
public:
    static constexpr std::uint8_t kBaseAddress = 0x70;
    static constexpr std::uint8_t kChannels = 8;
    static constexpr std::uint8_t kAllOff = 0x00;

    Tca9548a(I2cBus& bus, std::uint8_t address, GpioPort* gpio = nullptr,
             std::uint8_t resetPin = kNoPin);

    /* Відкритий канал живе рівно стільки, скільки потрібен: деструктор
       ізолює субшину сам, тож забути «зачинити» її неможливо. */
    class Channel {
    public:
        Channel(Channel&& other) noexcept;
        Channel(const Channel&) = delete;
        Channel& operator=(const Channel&) = delete;
        Channel& operator=(Channel&&) = delete;
        ~Channel();

        [[nodiscard]] std::uint8_t index() const noexcept { return index_; }

    private:
        friend class Tca9548a;
        Channel(Tca9548a& mux, std::uint8_t index) noexcept
            : mux_(&mux), index_(index) {}

        Tca9548a* mux_;
        std::uint8_t index_;
    };

    Result<void> begin();
    [[nodiscard]] Result<Channel> open(std::uint8_t channel);
    Result<void> isolate();
    [[nodiscard]] Result<std::uint8_t> controlByte();
    void hardReset();

    [[nodiscard]] std::uint8_t address() const noexcept { return address_; }
    [[nodiscard]] I2cBus& bus() const noexcept { return bus_; }

private:
    Result<void> writeControl(std::uint8_t mask);

    I2cBus& bus_;
    GpioPort* gpio_;
    std::uint8_t address_;
    std::uint8_t resetPin_;
    std::uint8_t shadow_{kAllOff};
    bool shadowValid_{false};
};

/* Банк комутаторів на спільній головній шині: до 8 чипів × 8 каналів. */
class MuxBank {
public:
    explicit MuxBank(std::span<Tca9548a> muxes) noexcept : muxes_(muxes) {}

    [[nodiscard]] std::size_t subbusCount() const noexcept {
        return muxes_.size() * Tca9548a::kChannels;
    }

    [[nodiscard]] Result<Tca9548a::Channel> open(std::uint8_t subbus);
    Result<void> isolateAll();

    struct PollResult {
        std::uint8_t ok;       /* скільки давачів відповіли */
        std::uint64_t failed;  /* біти субшин, які не відповіли */
    };

    /* Обійти всі субшини й прочитати той самий регістр однакових давачів. */
    PollResult poll(std::uint8_t device, std::uint8_t reg,
                    std::span<std::uint8_t> out, std::uint8_t len);

private:
    std::span<Tca9548a> muxes_;
};

}  // namespace board

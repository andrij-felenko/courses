// Сесія слота: монопольне володіння, консоль, послідовності живлення.
#pragma once

#include <chrono>
#include <filesystem>
#include <stdexcept>
#include <string_view>

#include "console.hpp"
#include "posix.hpp"
#include "programmer.hpp"
#include "rack_lines.hpp"

struct SlotBusy : std::runtime_error {
    using std::runtime_error::runtime_error;
};

class SlotSession {
public:
    // Захопити слот: чекає до wait, далі кидає SlotBusy.
    static SlotSession acquire(int slotId, std::chrono::milliseconds wait, int mirrorFd);

    void boot(std::string_view banner, std::chrono::milliseconds timeout);
    void flash(const std::filesystem::path& image);
    void unbrick();

    [[nodiscard]] Console& console() noexcept { return console_; }
    [[nodiscard]] int id() const noexcept { return slotId_; }

private:
    SlotSession(int slotId, UniqueFd lock, int mirrorFd);

    void powerCycle(std::chrono::milliseconds offFor);

    static constexpr auto kPowerOff = std::chrono::milliseconds{250};
    static constexpr auto kPowerSettle = std::chrono::milliseconds{30};
    static constexpr auto kBootRom = std::chrono::milliseconds{50};

    int slotId_;
    UniqueFd lock_;
    // ПОРЯДОК ОГОЛОШЕННЯ = ПОРЯДОК ІНІЦІАЛІЗАЦІЇ, і саме він тут канонічний:
    // консоль відкривається раніше за силові лінії, тому плата фізично не може
    // отримати живлення до того, як порт готовий приймати банер.
    Console console_;
    RackLines lines_;
    Programmer programmer_;
};

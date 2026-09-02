#pragma once

#include <cstdint>
#include <expected>
#include <span>

#include "peripherals.hpp"

namespace drv {

enum class SpiError : std::uint8_t {
    Timeout,     // блок мовчить: не той такт, не та ніжка, зависла лінія
    Overrun,     // OVR: приймач не встиг забрати попереднє слово
    ModeFault,   // MODF: зовнішній рівень на NSS зірвав роль ведучого
    Busy,        // попередній обмін ще в польоті
    BadLength    // буфери різної довжини або нульова довжина
};

class SpiMaster {
public:
    enum class Mode : std::uint8_t { Mode0, Mode1, Mode2, Mode3 };

    // baudDiv: 0..7, ділить f_PCLK2 на 2^(baudDiv+1)
    SpiMaster(mcu::SpiRegs& regs, Mode mode, std::uint8_t baudDiv) noexcept;

    // Тримає CS притиснутим, поки живий об'єкт: жодного шансу забути відпустити
    class Selection {
    public:
        explicit Selection(SpiMaster& owner) noexcept : owner_{owner} { owner_.selectChip(); }
        ~Selection() { owner_.releaseChip(); }
        Selection(const Selection&) = delete;
        Selection& operator=(const Selection&) = delete;

    private:
        SpiMaster& owner_;
    };

    [[nodiscard]] Selection select() noexcept { return Selection{*this}; }

    [[nodiscard]] std::expected<std::uint8_t, SpiError> transferByte(std::uint8_t value) noexcept;

    // Порожній rx означає "відповідь не потрібна", порожній tx — женемо 0xFF
    [[nodiscard]] std::expected<void, SpiError> transfer(std::span<const std::uint8_t> tx,
                                                        std::span<std::uint8_t> rx) noexcept;

    [[nodiscard]] std::expected<void, SpiError> waitIdle() noexcept;

    // Неблокувальний обмін; handler кличеться з контексту переривання
    using DoneHandler = void (*)(std::expected<void, SpiError>);

    // Обмін на перериваннях: у польоті рівно одне слово
    [[nodiscard]] std::expected<void, SpiError> startInterrupt(std::span<const std::uint8_t> tx,
                                                              std::span<std::uint8_t> rx,
                                                              DoneHandler handler) noexcept;
    void serviceInterrupt() noexcept;  // тіло обробника SPI1_IRQHandler

    [[nodiscard]] std::expected<void, SpiError> startDma(std::span<const std::uint8_t> tx,
                                                        std::span<std::uint8_t> rx,
                                                        DoneHandler handler) noexcept;
    [[nodiscard]] bool dmaBusy() const noexcept;

private:
    void selectChip() noexcept;
    void releaseChip() noexcept;
    void clearOverrun() noexcept;
    void recoverModeFault() noexcept;

    mcu::SpiRegs& regs_;
    static constexpr std::uint32_t pollBudget = 100000u;
};

}  // namespace drv

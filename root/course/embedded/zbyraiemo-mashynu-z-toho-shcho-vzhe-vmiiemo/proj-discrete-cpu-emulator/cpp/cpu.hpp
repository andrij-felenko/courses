// cpu.hpp — процесорне ядро: регістри й трифазний цикл Fetch-Decode-Execute.
//
// Ядро не знає про пам'ять нічого: воно вміє лише виставити адресу на шину
// й прийняти те, що звідти повернулося — включно з відмовою.
#pragma once

#include <cstdint>

#include "system_bus.hpp"

namespace emu {

enum class StopReason : std::uint8_t {
    Halted,     // дійшли до HALT — штатне завершення
    Fault,      // пастка: дешифратор не має рядка під цей опкод
    StepLimit   // сторожовий лічильник моделі
};

[[nodiscard]] constexpr std::string_view describe(StopReason reason) noexcept
{
    switch (reason) {
        case StopReason::Halted:    return "зупинено інструкцією HALT";
        case StopReason::Fault:     return "ПАСТКА: невідома інструкція";
        case StopReason::StepLimit: return "ПЕРЕРВАНО сторожовим лічильником";
    }
    return "невідомо";
}

class Cpu {
public:
    // Кожне поле — фізичний регістр на кристалі.
    struct Registers {
        std::uint16_t pc{0x0000};
        std::uint8_t  ir{0x00};
        std::uint8_t  acc{0x00};
        std::uint8_t  r0{0x00};
        bool          flag_z{false};   // результат АЛП дорівнює нулю
        bool          flag_c{false};   // перенесення (ADD) або позичка (SUB)
    };

    explicit Cpu(SystemBus& bus) noexcept : bus_{bus} {}

    // Апаратне скидання (Power-On Reset).
    void reset() noexcept;

    // Рівно один повний цикл Fetch-Decode-Execute.
    void step();

    // Крутить ядро, доки воно не стане або доки не вичерпається ліміт кроків.
    StopReason run(unsigned long max_steps = 200);

    [[nodiscard]] bool running() const noexcept { return !halted_ && !faulted_; }

    [[nodiscard]] const Registers& registers() const noexcept { return regs_; }
    [[nodiscard]] unsigned long    instructions() const noexcept { return instructions_; }
    [[nodiscard]] unsigned         bus_errors() const noexcept { return bus_errors_; }

    void set_trace(bool on) noexcept { trace_ = on; }

private:
    std::uint8_t  fetch_byte();                 // байт із потоку інструкцій, PC вперед
    std::uint16_t fetch_address();              // 16-бітний операнд, молодший байт уперед
    std::uint8_t  read_data(std::uint16_t addr);
    void          write_data(std::uint16_t addr, std::uint8_t data);
    void          report(BusFault fault, std::uint16_t addr);
    void          alu_store(std::uint16_t raw_result, bool carry_out) noexcept;
    void          logic_store(std::uint8_t result) noexcept;
    void          trace_instruction() const;

    SystemBus&    bus_;
    Registers     regs_{};
    bool          halted_{false};
    bool          faulted_{false};
    unsigned long instructions_{0};
    unsigned      bus_errors_{0};
    bool          trace_{true};
};

}  // namespace emu

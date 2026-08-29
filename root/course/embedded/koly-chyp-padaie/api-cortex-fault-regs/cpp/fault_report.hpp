// fault_report.hpp — налаштування діагностичного середовища ядра Cortex-M
// і розбір регістрів збою після аварії.
#pragma once

#include <cstdint>
#include <expected>
#include <optional>

namespace fault {

enum class Source : std::uint32_t {
    hard        = 0,
    mem_manage  = 1,
    bus         = 2,
    usage       = 3,
};

// Базовий кадр, який апаратура кладе на стек при вході у виняток.
// Порядок слів заданий архітектурою і змінам не підлягає.
struct ExceptionFrame {
    std::uint32_t r0;
    std::uint32_t r1;
    std::uint32_t r2;
    std::uint32_t r3;
    std::uint32_t r12;
    std::uint32_t lr;   // адреса повернення того, хто впав
    std::uint32_t pc;   // інструкція збою — для ТОЧНИХ помилок
    std::uint32_t psr;
};

// Значення LR при вході у виняток: псевдоадреса, біти якої кодують стан ядра.
class ExcReturn {
public:
    constexpr explicit ExcReturn(std::uint32_t raw) noexcept : raw_{raw} {}

    constexpr std::uint32_t raw() const noexcept { return raw_; }

    // Біт 3: впала звичайна програма (true) чи інше переривання (false).
    constexpr bool from_thread() const noexcept { return (raw_ & (1u << 3)) != 0u; }

    // Біт 2: кадр лежить на PSP (стек задачі) чи на MSP.
    constexpr bool uses_process_stack() const noexcept { return (raw_ & (1u << 2)) != 0u; }

    // Біт 4: базовий кадр із 8 слів (true) чи розширений із контекстом FPU.
    constexpr bool basic_frame() const noexcept { return (raw_ & (1u << 4)) != 0u; }

private:
    std::uint32_t raw_;
};

// Адресні регістри віддаються лише разом зі своїм прапорцем валідності:
// без MMARVALID / BFARVALID у них лежить сміття від попередніх аварій,
// і порожній optional — єдина чесна відповідь.
std::optional<std::uint32_t> mem_fault_address();
std::optional<std::uint32_t> bus_fault_address();

enum class ProbeError {
    bus_error,      // шина відповіла помилкою: адреси не існує
    unsafe_context, // не HardFault: BFHFNMIGN тут не діє, зондувати не можна
};

// Безпечне читання підозрілої адреси зсередини обробника HardFault.
std::expected<std::uint32_t, ProbeError> probe_read(std::uintptr_t address, Source source);

// Увімкнути роздільні обробники, апаратні пастки й точні помилки шини.
// Викликати якнайраніше в main(), до першого власного коду.
void init_diagnostics() noexcept;

[[noreturn]] void report(const ExceptionFrame& frame, ExcReturn lr, Source source);

}  // namespace fault

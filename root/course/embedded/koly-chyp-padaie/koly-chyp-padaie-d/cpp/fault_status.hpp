#pragma once

#include <cstdint>
#include <optional>
#include <string_view>

namespace fault {

// Базовий кадр, який апаратура ядра сама кладе на активний стек при вході
// у виняток. Порядок полів заданий архітектурою, міняти не можна.
struct ExceptionFrame {
    std::uint32_t r0;
    std::uint32_t r1;
    std::uint32_t r2;
    std::uint32_t r3;
    std::uint32_t r12;
    std::uint32_t lr;  // адреса повернення з функції, що впала
    std::uint32_t pc;  // адреса інструкції аварії — головне число звіту
    std::uint32_t psr;
};

enum class Vector : std::uint32_t { Hard = 0U, MemManage = 1U, Bus = 2U, Usage = 3U };

[[nodiscard]] std::string_view name_of(Vector vector) noexcept;

// Магічне значення LR на вході в обробник. Само по собі це не адреса,
// а опис того, звідки й куди ми повертаємось.
class ExcReturn {
public:
    constexpr explicit ExcReturn(std::uint32_t raw) noexcept : raw_{raw} {}

    [[nodiscard]] constexpr bool uses_process_stack() const noexcept { return (raw_ & 0x4U) != 0U; }
    [[nodiscard]] constexpr bool returns_to_thread() const noexcept { return (raw_ & 0x8U) != 0U; }
    [[nodiscard]] constexpr bool has_fpu_frame() const noexcept { return (raw_ & 0x10U) == 0U; }
    [[nodiscard]] constexpr std::uint32_t raw() const noexcept { return raw_; }

private:
    std::uint32_t raw_;
};

// Знімок HFSR і CFSR. Біти дійсності MMARVALID/BFARVALID природно лягають
// на optional: адреси або є, або її апаратура не зберегла.
class Status {
public:
    [[nodiscard]] static Status capture() noexcept;

    [[nodiscard]] std::uint32_t hfsr() const noexcept { return hfsr_; }
    [[nodiscard]] std::uint32_t cfsr() const noexcept { return cfsr_; }

    [[nodiscard]] std::optional<std::uint32_t> memmanage_address() const noexcept;
    [[nodiscard]] std::optional<std::uint32_t> bus_address() const noexcept;

    // Один рядок про те, куди дивитися далі.
    [[nodiscard]] std::string_view hint() const noexcept;

    void print() const;

    // Прапорці статусу скидаються записом одиниці у вже встановлені біти.
    void clear() const noexcept;

private:
    std::uint32_t hfsr_{};
    std::uint32_t cfsr_{};
};

// Кадр віддається лише з адреси, яка справді схожа на стек. Якщо аварія
// сталася саме через зруйнований SP, сліпе розіменування дало б другий збій
// усередині обробника — а це вже Lockup.
[[nodiscard]] const ExceptionFrame* frame_at(std::uint32_t stack_pointer) noexcept;

// Вмикає індивідуальні обробники MemManage/BusFault/UsageFault, пастки
// ділення на нуль і невирівняного доступу, вимикає буфер запису шини.
void enable_all_handlers() noexcept;

// Повний звіт про аварію: кадр, EXC_RETURN, статусні регістри, підказка.
void report(std::uint32_t stack_pointer, ExcReturn exc_return, Vector vector);

} // namespace fault

// fault.hpp — кадр винятку й розбір причини збою.
//
// Розбір CFSR — чиста функція від двох чисел, тож він constexpr: той самий код
// судить і живий збій у прошивці, і значення регістрів, вставлені в static_assert
// під час розбору чужого лога. Відсутність адреси доступу виражена
// std::optional, а не парою «число + прапорець»: без MMARVALID чи BFARVALID у
// регістрі лежить значення від минулого разу, і цю відмінність не можна
// втратити дорогою.

#pragma once

#include <cstdint>
#include <optional>
#include <string_view>

namespace mcu {

// Кадр, який ядро уклало на стек апаратно. Порядок полів заданий архітектурою.
struct ExceptionFrame {
    std::uint32_t r0;
    std::uint32_t r1;
    std::uint32_t r2;
    std::uint32_t r3;
    std::uint32_t r12;
    std::uint32_t lr;   // адреса повернення з функції, що впала
    std::uint32_t pc;   // інструкція, на якій стався збій
    std::uint32_t psr;
};

enum class FaultCause : std::uint8_t {
    unknown,
    divide_by_zero,
    unaligned_access,
    no_coprocessor,
    invalid_state,
    invalid_exc_return,
    undefined_instruction,
    precise_bus_error,
    imprecise_bus_error,
    instruction_bus_error,
    data_access_violation,
    instruction_access_violation,
    stacking_error,
    unstacking_error,
    vector_table_read_error,
    debug_event,
};

namespace cfsr_bits {
inline constexpr std::uint32_t mmarvalid   = 1u << 7;
inline constexpr std::uint32_t mstkerr     = 1u << 4;
inline constexpr std::uint32_t munstkerr   = 1u << 3;
inline constexpr std::uint32_t daccviol    = 1u << 1;
inline constexpr std::uint32_t iaccviol    = 1u << 0;
inline constexpr std::uint32_t bfarvalid   = 1u << 15;
inline constexpr std::uint32_t impreciserr = 1u << 10;
inline constexpr std::uint32_t preciserr   = 1u << 9;
inline constexpr std::uint32_t ibuserr     = 1u << 8;
inline constexpr std::uint32_t divbyzero   = 1u << 25;
inline constexpr std::uint32_t unaligned   = 1u << 24;
inline constexpr std::uint32_t nocp        = 1u << 19;
inline constexpr std::uint32_t invpc       = 1u << 18;
inline constexpr std::uint32_t invstate    = 1u << 17;
inline constexpr std::uint32_t undefinstr  = 1u << 16;
}  // namespace cfsr_bits

namespace hfsr_bits {
inline constexpr std::uint32_t vecttbl  = 1u << 1;
inline constexpr std::uint32_t forced    = 1u << 30;
inline constexpr std::uint32_t debugevt  = 1u << 31;
}  // namespace hfsr_bits

// Розбір згори вниз: ознаки липкі й накопичуються, тож першою перевіряється та,
// що точно вказує на винну інструкцію.
constexpr FaultCause decode_cause(std::uint32_t cfsr, std::uint32_t hfsr) noexcept
{
    using namespace cfsr_bits;
    if (cfsr & divbyzero)   { return FaultCause::divide_by_zero; }
    if (cfsr & unaligned)   { return FaultCause::unaligned_access; }
    if (cfsr & nocp)        { return FaultCause::no_coprocessor; }
    if (cfsr & invstate)    { return FaultCause::invalid_state; }
    if (cfsr & invpc)       { return FaultCause::invalid_exc_return; }
    if (cfsr & undefinstr)  { return FaultCause::undefined_instruction; }
    if (cfsr & preciserr)   { return FaultCause::precise_bus_error; }
    if (cfsr & impreciserr) { return FaultCause::imprecise_bus_error; }
    if (cfsr & ibuserr)     { return FaultCause::instruction_bus_error; }
    if (cfsr & daccviol)    { return FaultCause::data_access_violation; }
    if (cfsr & iaccviol)    { return FaultCause::instruction_access_violation; }
    if (cfsr & mstkerr)     { return FaultCause::stacking_error; }
    if (cfsr & munstkerr)   { return FaultCause::unstacking_error; }
    if (hfsr & hfsr_bits::vecttbl)  { return FaultCause::vector_table_read_error; }
    if (hfsr & hfsr_bits::debugevt) { return FaultCause::debug_event; }
    return FaultCause::unknown;
}

constexpr std::string_view describe(FaultCause cause) noexcept
{
    switch (cause) {
    case FaultCause::divide_by_zero:      return "ділення цілого на нуль";
    case FaultCause::unaligned_access:    return "невирівняний доступ";
    case FaultCause::no_coprocessor:      return "інструкція FPU при вимкненому співпроцесорі";
    case FaultCause::invalid_state:       return "стрибок за адресою без Thumb-біта";
    case FaultCause::invalid_exc_return:  return "невірне значення EXC_RETURN";
    case FaultCause::undefined_instruction: return "невідома інструкція";
    case FaultCause::precise_bus_error:   return "точна помилка шини (адреса в BFAR)";
    case FaultCause::imprecise_bus_error: return "неточна помилка шини: винна відкладена запис-операція";
    case FaultCause::instruction_bus_error: return "помилка шини при вибірці коду";
    case FaultCause::data_access_violation: return "заборонений доступ до даних (MPU)";
    case FaultCause::instruction_access_violation: return "вибірка коду із забороненої зони (MPU)";
    case FaultCause::stacking_error:      return "збій при укладанні кадру: переповнення стека";
    case FaultCause::unstacking_error:    return "збій при знятті кадру винятку";
    case FaultCause::vector_table_read_error: return "нечитний запис векторної таблиці";
    case FaultCause::debug_event:         return "подія налагодження";
    case FaultCause::unknown:             break;
    }
    return "причина не позначена в CFSR/HFSR";
}

// Адреса доступу дійсна лише тоді, коли залізо саме сказало, що зафіксувало її.
constexpr std::optional<std::uint32_t> access_address(std::uint32_t cfsr,
                                                      std::uint32_t mmfar,
                                                      std::uint32_t bfar) noexcept
{
    if (cfsr & cfsr_bits::mmarvalid) { return mmfar; }
    if (cfsr & cfsr_bits::bfarvalid) { return bfar; }
    return std::nullopt;
}

struct FaultReport {
    ExceptionFrame frame{};
    std::uint32_t exception{};   // номер вектора з ICSR
    std::uint32_t cfsr{};
    std::uint32_t hfsr{};
    std::optional<std::uint32_t> address{};
    FaultCause cause{FaultCause::unknown};
    bool used_psp{};    // кадр лежав на стеку задачі
    bool escalated{};   // збій ескалював у HardFault

    constexpr std::string_view cause_text() const noexcept { return describe(cause); }
};

// Останній зафіксований збій. Лежить у .bss, тож переживає лише поточний сеанс:
// після скидання стартовий код занулює цю пам'ять. Під GDB звіт читається
// командою `print mcu::last_fault`.
inline FaultReport last_fault{};

// Перевірка розбору без заліза: значення CFSR узяте з живого ділення на нуль.
static_assert(decode_cause(cfsr_bits::divbyzero, 0) == FaultCause::divide_by_zero);
static_assert(!access_address(cfsr_bits::divbyzero, 0xDEADBEEF, 0xDEADBEEF).has_value());

}  // namespace mcu

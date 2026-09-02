#pragma once

/*
 * Посмертний розбір помилок ядра.
 *
 * Довідник описує ескалацію словами: поки стоїть маска, настроюваний обробник
 * (MemManage, BusFault, UsageFault) виконатися не може, і апаратура підмінює
 * його HardFault-ом із пріоритетом -1. Цей модуль перетворює ту підміну на
 * запис, який переживає скидання, і відповідає на одне питання:
 *
 *     помилка сталася ВСЕРЕДИНІ критичної секції чи поза нею?
 *
 * Випадок FAULTMASK сюди не потрапляє: помилка під FAULTMASK — це Lockup
 * State, ядро припиняє вибірку інструкцій, і жоден обробник не запускається.
 */

#include "cortexm_regs.hpp"

#include <cstdint>
#include <optional>
#include <string_view>

namespace cortexm {

enum class FaultKind : std::uint32_t {
    Hard      = 0,
    MemManage = 1,
    Bus       = 2,
    Usage     = 3
};

[[nodiscard]] std::string_view to_string(FaultKind kind) noexcept;

/*
 * Кадр, який апаратура складає на стек перед входом у обробник. Порядок
 * полів заданий архітектурою. Регістри r4..r11 сюди не входять — їх зберігає
 * викликана функція, а не апаратура.
 */
struct ExceptionFrame {
    std::uint32_t r0;
    std::uint32_t r1;
    std::uint32_t r2;
    std::uint32_t r3;
    std::uint32_t r12;
    std::uint32_t lr;     /* адреса повернення того, хто викликав винуватця */
    std::uint32_t pc;     /* інструкція, на якій усе сталося                */
    std::uint32_t xpsr;   /* біт 9 = 1: вставлено 4 байти вирівнювання      */
};

/* Стан трьох масок у момент помилки — вхід у виключення їх не змінює. */
struct MaskSnapshot {
    regs::PrimaskState primask;
    regs::FaultmaskState faultmask;
    std::uint32_t basepri;

    /*
     * BASEPRI враховуємо нарівні з PRIMASK: поріг маскує й настроювані
     * обробники помилок, якщо їхній пріоритет чисельно не менший за нього.
     */
    [[nodiscard]] constexpr bool any_masked() const noexcept
    {
        return primask != regs::PrimaskState::Enabled
            || faultmask != regs::FaultmaskState::Enabled
            || basepri != 0U;
    }
};

/*
 * Тип навмисно тривіальний: запис живе в секції, яку стартовий код не чистить,
 * і будь-який ініціалізатор чи нетривіальний конструктор затер би його на
 * старті — тобто рівно тоді, коли він потрібен. static_assert-и нижче стежать,
 * щоб ця властивість не загубилася при першій же «зручній» правці.
 */
struct FaultRecord {
    FaultKind kind;
    std::uint32_t exc_return;   /* біт 2: кадр на PSP; біт 3: перервано Thread */

    std::uint32_t hfsr;         /* FORCED, VECTTBL, DEBUGEVT */
    std::uint32_t cfsr;         /* MMFSR[7:0] | BFSR[15:8] | UFSR[31:16] */
    std::uint32_t mmfar;
    std::uint32_t bfar;
    bool mmfar_valid;
    bool bfar_valid;

    MaskSnapshot masks;
    ExceptionFrame frame;

    /* HFSR.FORCED — апаратура підмінила настроюваний обробник HardFault-ом. */
    [[nodiscard]] bool escalated() const noexcept;

    /* Та сама підміна, але доведено спричинена відкритою критичною секцією. */
    [[nodiscard]] bool inside_critical_section() const noexcept
    {
        return escalated() && masks.any_masked();
    }

    /* Кадр лежав на PSP — виключення застало задачу RTOS, а не фон. */
    [[nodiscard]] constexpr bool from_process_stack() const noexcept
    {
        return (exc_return & 0x4U) != 0U;
    }

    /*
     * Адреса збою, якщо апаратура її зафіксувала. Порожньо для неточної
     * помилки шини: там запис завис у буфері, BFAR не заповнюється, а PC у
     * кадрі показує вже наступні інструкції.
     */
    [[nodiscard]] std::optional<std::uint32_t> fault_address() const noexcept;

    /* Причина людською мовою: перший встановлений біт у порядку розбору. */
    [[nodiscard]] std::string_view cause() const noexcept;
};

/*
 * Забирає запис попереднього запуску й одразу позначає його прочитаним:
 * один збій розбирається рівно один раз, і повторне завантаження вже нічого
 * не знайде.
 */
[[nodiscard]] std::optional<FaultRecord> take_last_fault() noexcept;

/*
 * Вмикає настроювані обробники помилок і пастку ділення на нуль. Без цього
 * MemManage, BusFault та UsageFault як окремі виключення не існують: усе
 * приходить HardFault-ом одразу, і біт FORCED уже нічого не розрізняє.
 */
void enable_configurable_faults() noexcept;

}  // namespace cortexm

/* Точка входу з асемблерного прологу asm/fault_entry.S. Не повертається. */
extern "C" void fault_entry_to_c(const cortexm::ExceptionFrame* frame,
                                 std::uint32_t exc_return,
                                 std::uint32_t kind);

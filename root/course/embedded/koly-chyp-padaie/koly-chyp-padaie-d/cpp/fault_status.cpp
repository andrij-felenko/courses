#include "fault_status.hpp"

#include <array>

#include "bitnames.hpp"
#include "trace.hpp"
#include "stm32f4xx.h"

namespace fault {
namespace {

using diag::BitName;

constexpr std::array kHfsrBits{
    BitName{SCB_HFSR_DEBUGEVT_Msk, "DEBUGEVT подія налагодження (breakpoint/watchpoint)"},
    BitName{SCB_HFSR_FORCED_Msk, "FORCED   ескалація: справжня причина в CFSR"},
    BitName{SCB_HFSR_VECTTBL_Msk, "VECTTBL  помилка читання таблиці векторів (перевір VTOR)"},
};

constexpr std::array kMemManageBits{
    BitName{SCB_CFSR_IACCVIOL_Msk, "IACCVIOL   вибірка коду з області XN"},
    BitName{SCB_CFSR_DACCVIOL_Msk, "DACCVIOL   заборонений доступ до даних (MPU)"},
    BitName{SCB_CFSR_MUNSTKERR_Msk, "MUNSTKERR  збій зняття кадру зі стека"},
    BitName{SCB_CFSR_MSTKERR_Msk, "MSTKERR    збій укладання кадру — типове переповнення стека"},
    BitName{SCB_CFSR_MLSPERR_Msk, "MLSPERR    збій лінивого збереження регістрів FPU"},
};

constexpr std::array kBusBits{
    BitName{SCB_CFSR_IBUSERR_Msk, "IBUSERR      помилка шини при вибірці інструкції"},
    BitName{SCB_CFSR_PRECISERR_Msk, "PRECISERR    точна помилка: PC вказує на винну інструкцію"},
    BitName{SCB_CFSR_IMPRECISERR_Msk, "IMPRECISERR  неточна помилка: PC зсунуто буфером запису"},
    BitName{SCB_CFSR_UNSTKERR_Msk, "UNSTKERR     збій шини при знятті кадру"},
    BitName{SCB_CFSR_STKERR_Msk, "STKERR       збій шини при укладанні кадру"},
    BitName{SCB_CFSR_LSPERR_Msk, "LSPERR       збій шини при збереженні регістрів FPU"},
};

constexpr std::array kUsageBits{
    BitName{SCB_CFSR_UNDEFINSTR_Msk, "UNDEFINSTR  невідомий опкод: перехід у дані або затертий стек"},
    BitName{SCB_CFSR_INVSTATE_Msk, "INVSTATE    втрачено біт Thumb: парна адреса переходу"},
    BitName{SCB_CFSR_INVPC_Msk, "INVPC       пошкоджений EXC_RETURN при виході з переривання"},
    BitName{SCB_CFSR_NOCP_Msk, "NOCP        інструкція FPU при вимкненому співпроцесорі (CPACR)"},
    BitName{SCB_CFSR_UNALIGNED_Msk, "UNALIGNED   невирівняний доступ"},
    BitName{SCB_CFSR_DIVBYZERO_Msk, "DIVBYZERO   ділення на нуль"},
};

// Межі пам'яті STM32F407: основна SRAM і окремий блок CCM.
constexpr std::uint32_t kSramBegin = 0x2000'0000U;
constexpr std::uint32_t kSramEnd   = 0x2002'0000U;
constexpr std::uint32_t kCcmBegin  = 0x1000'0000U;
constexpr std::uint32_t kCcmEnd    = 0x1001'0000U;

void print_group(std::string_view title, std::span<const BitName> table, std::uint32_t value)
{
    trace::out.line(title, ": ", trace::Hex{value});

    if (!diag::any_set(table, value)) {
        trace::out.line("    - (жодного біта)");
        return;
    }
    diag::for_each_set(table, value, [](std::string_view text) { trace::out.line("    - ", text); });
}

} // namespace

std::string_view name_of(Vector vector) noexcept
{
    switch (vector) {
    case Vector::Hard:      return "HardFault";
    case Vector::MemManage: return "MemManage";
    case Vector::Bus:       return "BusFault";
    case Vector::Usage:     return "UsageFault";
    }
    return "невідомий вектор";
}

Status Status::capture() noexcept
{
    Status status;
    status.hfsr_ = SCB->HFSR;
    status.cfsr_ = SCB->CFSR;
    return status;
}

std::optional<std::uint32_t> Status::memmanage_address() const noexcept
{
    if ((cfsr_ & SCB_CFSR_MMARVALID_Msk) == 0U) {
        return std::nullopt;
    }
    return SCB->MMFAR;
}

std::optional<std::uint32_t> Status::bus_address() const noexcept
{
    if ((cfsr_ & SCB_CFSR_BFARVALID_Msk) == 0U) {
        return std::nullopt;
    }
    return SCB->BFAR;
}

std::string_view Status::hint() const noexcept
{
    if ((cfsr_ & (SCB_CFSR_MSTKERR_Msk | SCB_CFSR_UNDEFINSTR_Msk | SCB_CFSR_INVSTATE_Msk)) != 0U) {
        return "перевір глибину стека й покажчики на функції";
    }
    if ((cfsr_ & SCB_CFSR_IMPRECISERR_Msk) != 0U) {
        return "звертання до периферії без тактування; повтори з DISDEFWBUF=1";
    }
    if ((cfsr_ & SCB_CFSR_PRECISERR_Msk) != 0U) {
        return "дивись BFAR: нульовий покажчик або чужа адреса";
    }
    if ((cfsr_ & SCB_CFSR_DACCVIOL_Msk) != 0U) {
        return "порушення прав MPU: перевір регіони й покажчики на NULL";
    }
    if ((cfsr_ & SCB_CFSR_UNALIGNED_Msk) != 0U) {
        return "невирівняне приведення буфера до покажчика на слово";
    }
    if ((cfsr_ & SCB_CFSR_DIVBYZERO_Msk) != 0U) {
        return "нульовий дільник у цілочисловому діленні";
    }
    return "CFSR порожній — дивись HFSR.VECTTBL і цілість VTOR";
}

void Status::print() const
{
    print_group("HFSR", kHfsrBits, hfsr_);
    print_group("MMFSR", kMemManageBits, cfsr_ & 0x0000'00FFU);
    print_group("BFSR", kBusBits, cfsr_ & 0x0000'FF00U);
    print_group("UFSR", kUsageBits, cfsr_ & 0xFFFF'0000U);

    if (const std::optional<std::uint32_t> address = memmanage_address()) {
        trace::out.line("MMFAR=", trace::Hex{*address});
    } else {
        trace::out.line("MMFAR: недійсний (MMARVALID=0)");
    }

    if (const std::optional<std::uint32_t> address = bus_address()) {
        trace::out.line("BFAR =", trace::Hex{*address});
    } else {
        trace::out.line("BFAR: недійсний (BFARVALID=0)");
    }

    trace::out.line("підказка: ", hint());
}

void Status::clear() const noexcept
{
    SCB->HFSR = hfsr_;
    SCB->CFSR = cfsr_;
}

const ExceptionFrame* frame_at(std::uint32_t stack_pointer) noexcept
{
    constexpr std::uint32_t size = sizeof(ExceptionFrame);

    if ((stack_pointer & 0x3U) != 0U) {
        return nullptr;
    }
    const bool in_sram = stack_pointer >= kSramBegin && stack_pointer + size <= kSramEnd;
    const bool in_ccm  = stack_pointer >= kCcmBegin && stack_pointer + size <= kCcmEnd;
    if (!in_sram && !in_ccm) {
        return nullptr;
    }
    return reinterpret_cast<const ExceptionFrame*>(stack_pointer);
}

void enable_all_handlers() noexcept
{
    // Після скидання всі три конфігуровані винятки вимкнені, і будь-яка помилка
    // ескалується в HardFault із бітом HFSR.FORCED.
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk | SCB_SHCSR_BUSFAULTENA_Msk | SCB_SHCSR_USGFAULTENA_Msk;

    // Ділення на нуль і невирівняний доступ за замовчуванням мовчать.
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk | SCB_CCR_UNALIGN_TRP_Msk;

    // ACTLR у CMSIS лежить у блоці SCnSCB. DISDEFWBUF вимикає буфер запису:
    // кожен STR у периферію стає синхронним, тож помилка шини приходить точною,
    // а BFAR містить справжню адресу. Ціна — повільніший запис, тому в серійній
    // прошивці цей біт лишають вимкненим.
    SCnSCB->ACTLR |= SCnSCB_ACTLR_DISDEFWBUF_Msk;

    __DSB();
    __ISB();
}

void report(std::uint32_t stack_pointer, ExcReturn exc_return, Vector vector)
{
    const Status status = Status::capture();

    trace::out.line("\r\n!!! ", name_of(vector), " !!!");
    trace::out.line("EXC_RETURN=", trace::Hex{exc_return.raw()});
    trace::out.line("    стек аварії: ",
                    exc_return.uses_process_stack() ? "PSP (задача RTOS)"
                                                    : "MSP (головний стек або переривання)");
    trace::out.line("    режим до збою: ",
                    exc_return.returns_to_thread() ? "Thread"
                                                   : "Handler (збій усередині переривання)");
    trace::out.line("    кадр FPU: ",
                    exc_return.has_fpu_frame() ? "розширений (+18 слів S0-S15, FPSCR)"
                                               : "базовий (8 слів)");
    trace::out.line("frame SP=", trace::Hex{stack_pointer});

    if (const ExceptionFrame* frame = frame_at(stack_pointer)) {
        trace::out.line("  R0 =", trace::Hex{frame->r0});
        trace::out.line("  R1 =", trace::Hex{frame->r1});
        trace::out.line("  R2 =", trace::Hex{frame->r2});
        trace::out.line("  R3 =", trace::Hex{frame->r3});
        trace::out.line("  R12=", trace::Hex{frame->r12});
        trace::out.line("  LR =", trace::Hex{frame->lr});
        trace::out.line("  PC =", trace::Hex{frame->pc});
        trace::out.line("  PSR=", trace::Hex{frame->psr});
        // Номер активного винятку в мить аварії: 0 — код задачі, інше — переривання.
        trace::out.line("  IPSR=", trace::Hex{frame->psr & 0x1FFU});
        trace::out.line("addr2line: arm-none-eabi-addr2line -e firmware.elf -f -C -a ",
                        trace::Hex{frame->pc});
    } else {
        // Сам SP зруйновано — це вже діагноз: переповнення стека або чужий запис.
        trace::out.line("кадр недоступний: SP не вказує на RAM (переповнення стека?)");
    }

    status.print();
    status.clear();
}

} // namespace fault

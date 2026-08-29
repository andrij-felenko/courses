#include "fault_decode.hpp"

#include <array>
#include <span>

#include "stm32f4xx.h"
#include "sync_uart.hpp"

namespace crash {
namespace {

using io::console::newline;
using io::console::write;
using io::console::write_dec;
using io::console::write_hex;

// Прапорці RCC->CSR за RM0090. Іменні макроси в різних версіях заголовків
// звуться по-різному (PINRSTF проти PADRSTF), тому тримаємо свої константи.
constexpr std::array kResetFlags{
    FlagName{1u << 31, "LPWR (вихід зі сну зіпсовано)"},
    FlagName{1u << 30, "WWDG (віконний сторожовий)"},
    FlagName{1u << 29, "IWDG (незалежний сторожовий)"},
    FlagName{1u << 28, "SOFT (NVIC_SystemReset)"},
    FlagName{1u << 27, "POR/PDR (подача живлення)"},
    FlagName{1u << 26, "PIN (кнопка NRST)"},
    FlagName{1u << 25, "BOR (просадка живлення)"},
};

constexpr std::array kHardFaultFlags{
    FlagName{SCB_HFSR_VECTTBL_Msk, "VECTTBL (збій читання таблиці векторів)"},
    FlagName{SCB_HFSR_FORCED_Msk, "FORCED (ескалація з іншого винятку)"},
    FlagName{SCB_HFSR_DEBUGEVT_Msk, "DEBUGEVT"},
};

constexpr std::array kMemManageFlags{
    FlagName{SCB_CFSR_IACCVIOL_Msk, "IACCVIOL (виконання із забороненої області)"},
    FlagName{SCB_CFSR_DACCVIOL_Msk, "DACCVIOL (доступ до даних заборонено MPU)"},
    FlagName{SCB_CFSR_MUNSTKERR_Msk, "MUNSTKERR (збій під час розкручування стека)"},
    FlagName{SCB_CFSR_MSTKERR_Msk, "MSTKERR (збій укладання кадру — схоже на переповнення стека)"},
    FlagName{SCB_CFSR_MLSPERR_Msk, "MLSPERR (збій лінивого збереження FPU)"},
};

constexpr std::array kBusFaultFlags{
    FlagName{SCB_CFSR_IBUSERR_Msk, "IBUSERR (вибірка інструкції з неіснуючої адреси)"},
    FlagName{SCB_CFSR_PRECISERR_Msk, "PRECISERR (точна помилка шини, адреса в BFAR)"},
    FlagName{SCB_CFSR_IMPRECISERR_Msk, "IMPRECISERR (відкладений запис, адреси немає)"},
    FlagName{SCB_CFSR_UNSTKERR_Msk, "UNSTKERR"},
    FlagName{SCB_CFSR_STKERR_Msk, "STKERR (стек виліз за межі RAM)"},
    FlagName{SCB_CFSR_LSPERR_Msk, "LSPERR"},
};

constexpr std::array kUsageFaultFlags{
    FlagName{SCB_CFSR_UNDEFINSTR_Msk, "UNDEFINSTR (невідома інструкція — зіпсований код)"},
    FlagName{SCB_CFSR_INVSTATE_Msk, "INVSTATE (перехід за адресою без біта Thumb)"},
    FlagName{SCB_CFSR_INVPC_Msk, "INVPC (зіпсований EXC_RETURN або кадр)"},
    FlagName{SCB_CFSR_NOCP_Msk, "NOCP (FPU-інструкція при вимкненому співпроцесорі)"},
    FlagName{SCB_CFSR_UNALIGNED_Msk, "UNALIGNED (невирівняний доступ)"},
    FlagName{SCB_CFSR_DIVBYZERO_Msk, "DIVBYZERO (ділення на нуль)"},
};

void print_flags(std::uint32_t value, std::span<const FlagName> table)
{
    bool any = false;
    for (const FlagName& flag : table) {
        if ((value & flag.mask) != 0) {
            static_cast<void>(write("      - "));
            static_cast<void>(write(flag.name));
            static_cast<void>(newline());
            any = true;
        }
    }
    if (!any) {
        static_cast<void>(write("      - (жодного біта)\r\n"));
    }
}

void print_reg(std::string_view name, std::uint32_t value)
{
    static_cast<void>(write("  "));
    static_cast<void>(write(name));
    static_cast<void>(write(" = "));
    static_cast<void>(write_hex(value));
    static_cast<void>(newline());
}

void print_fpu(const Record& record)
{
    switch (record.fpu) {
    case FpuFrame::None:
        static_cast<void>(write("  FPU: базовий кадр, співпроцесор не задіяно\r\n"));
        return;
    case FpuFrame::LazyPending:
        static_cast<void>(write("  FPU: розширений кадр, але S0-S15 ще не збережено\r\n"));
        return;
    case FpuFrame::Saved:
        print_reg("FPSCR", record.fpscr);
        for (std::size_t i = 0; i < record.s.size(); ++i) {
            static_cast<void>(write("  S"));
            static_cast<void>(write_dec(static_cast<std::uint32_t>(i)));
            static_cast<void>(write(" = "));
            static_cast<void>(write_hex(record.s[i]));
            static_cast<void>(newline());
        }
        return;
    }
    static_cast<void>(write("  FPU: стан невідомий\r\n"));
}

} // namespace

void print_reset_cause(std::uint32_t rcc_csr)
{
    static_cast<void>(write("[reset] причина:\r\n"));
    print_flags(rcc_csr, kResetFlags);
}

void print(const Record& record)
{
    static_cast<void>(write("[crash] дамп знайдено, падінь поспіль: "));
    static_cast<void>(write_dec(record.crash_count));
    static_cast<void>(newline());

    // Перше, на що дивляться: PC — де зупинилося, LR — звідки прийшли.
    print_reg("PC ", record.frame.pc);
    print_reg("LR ", record.frame.lr);
    print_reg("PSR", record.frame.psr);
    print_reg("R0 ", record.frame.r0);
    print_reg("R1 ", record.frame.r1);
    print_reg("R2 ", record.frame.r2);
    print_reg("R3 ", record.frame.r3);
    print_reg("R12", record.frame.r12);

    static_cast<void>(write("  стек аварії: "));
    static_cast<void>(write((record.exc_return & (1u << 2)) != 0
                                ? "PSP (код задачі)\r\n"
                                : "MSP (обробник або bare-metal)\r\n"));

    print_reg("EXC_RETURN", record.exc_return);
    print_reg("SHCSR", record.shcsr);

    print_reg("HFSR", record.hfsr);
    print_flags(record.hfsr, kHardFaultFlags);

    print_reg("CFSR", record.cfsr);
    static_cast<void>(write("    MemManage:\r\n"));
    print_flags(record.cfsr, kMemManageFlags);
    static_cast<void>(write("    BusFault:\r\n"));
    print_flags(record.cfsr, kBusFaultFlags);
    static_cast<void>(write("    UsageFault:\r\n"));
    print_flags(record.cfsr, kUsageFaultFlags);

    // Адресні регістри мають сенс лише разом зі своїм бітом дійсності: без
    // нього там лежить адреса якоїсь минулої, давно забутої помилки.
    if ((record.cfsr & SCB_CFSR_MMARVALID_Msk) != 0) {
        print_reg("MMFAR (адреса порушення MPU)", record.mmfar);
    }
    if ((record.cfsr & SCB_CFSR_BFARVALID_Msk) != 0) {
        print_reg("BFAR (адреса помилки шини)", record.bfar);
    }

    print_fpu(record);
}

} // namespace crash

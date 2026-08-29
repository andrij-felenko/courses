#include "fault_report.h"

#include <stddef.h>

#include "stm32f4xx.h"
#include "uart_sync.h"

// Прапорці RCC->CSR за RM0090. Іменні макроси в різних версіях заголовків
// звуться по-різному (PINRSTF проти PADRSTF), тому тримаємо свої константи.
#define RST_LPWR (1u << 31)
#define RST_WWDG (1u << 30)
#define RST_IWDG (1u << 29)
#define RST_SOFT (1u << 28)
#define RST_POR (1u << 27)
#define RST_PIN (1u << 26)
#define RST_BOR (1u << 25)

typedef struct {
    uint32_t mask;
    const char *name;
} bit_name_t;

static const bit_name_t k_reset_flags[] = {
    {RST_LPWR, "LPWR (вихід зі сну зіпсовано)"},
    {RST_WWDG, "WWDG (віконний сторожовий)"},
    {RST_IWDG, "IWDG (незалежний сторожовий)"},
    {RST_SOFT, "SOFT (NVIC_SystemReset)"},
    {RST_POR, "POR/PDR (подача живлення)"},
    {RST_PIN, "PIN (кнопка NRST)"},
    {RST_BOR, "BOR (просадка живлення)"},
};

static const bit_name_t k_hfsr_bits[] = {
    {SCB_HFSR_VECTTBL_Msk, "VECTTBL (збій читання таблиці векторів)"},
    {SCB_HFSR_FORCED_Msk, "FORCED (ескалація з іншого винятку)"},
    {SCB_HFSR_DEBUGEVT_Msk, "DEBUGEVT"},
};

static const bit_name_t k_mem_bits[] = {
    {SCB_CFSR_IACCVIOL_Msk, "IACCVIOL (виконання із забороненої області)"},
    {SCB_CFSR_DACCVIOL_Msk, "DACCVIOL (доступ до даних заборонено MPU)"},
    {SCB_CFSR_MUNSTKERR_Msk, "MUNSTKERR (збій під час розкручування стека)"},
    {SCB_CFSR_MSTKERR_Msk, "MSTKERR (збій укладання кадру — схоже на переповнення стека)"},
    {SCB_CFSR_MLSPERR_Msk, "MLSPERR (збій лінивого збереження FPU)"},
};

static const bit_name_t k_bus_bits[] = {
    {SCB_CFSR_IBUSERR_Msk, "IBUSERR (вибірка інструкції з неіснуючої адреси)"},
    {SCB_CFSR_PRECISERR_Msk, "PRECISERR (точна помилка шини, адреса в BFAR)"},
    {SCB_CFSR_IMPRECISERR_Msk, "IMPRECISERR (відкладений запис, адреси немає)"},
    {SCB_CFSR_UNSTKERR_Msk, "UNSTKERR"},
    {SCB_CFSR_STKERR_Msk, "STKERR (стек виліз за межі RAM)"},
    {SCB_CFSR_LSPERR_Msk, "LSPERR"},
};

static const bit_name_t k_usage_bits[] = {
    {SCB_CFSR_UNDEFINSTR_Msk, "UNDEFINSTR (невідома інструкція — зіпсований код)"},
    {SCB_CFSR_INVSTATE_Msk, "INVSTATE (перехід за адресою без біта Thumb)"},
    {SCB_CFSR_INVPC_Msk, "INVPC (зіпсований EXC_RETURN або кадр)"},
    {SCB_CFSR_NOCP_Msk, "NOCP (FPU-інструкція при вимкненому співпроцесорі)"},
    {SCB_CFSR_UNALIGNED_Msk, "UNALIGNED (невирівняний доступ)"},
    {SCB_CFSR_DIVBYZERO_Msk, "DIVBYZERO (ділення на нуль)"},
};

static void print_named_bits(uint32_t value, const bit_name_t *table, size_t count)
{
    int printed = 0;
    for (size_t i = 0; i < count; ++i) {
        if ((value & table[i].mask) != 0u) {
            (void)uart_sync_write("      - ");
            (void)uart_sync_write(table[i].name);
            (void)uart_sync_newline();
            printed = 1;
        }
    }
    if (!printed) {
        (void)uart_sync_write("      - (жодного біта)\r\n");
    }
}

static void print_reg(const char *name, uint32_t value)
{
    (void)uart_sync_write("  ");
    (void)uart_sync_write(name);
    (void)uart_sync_write(" = ");
    (void)uart_sync_hex32(value);
    (void)uart_sync_newline();
}

void fault_report_reset_cause(uint32_t rcc_csr)
{
    (void)uart_sync_write("[reset] причина:\r\n");
    print_named_bits(rcc_csr, k_reset_flags,
                     sizeof(k_reset_flags) / sizeof(k_reset_flags[0]));
}

void fault_report_dump(const crash_dump_t *dump)
{
    (void)uart_sync_write("[crash] дамп знайдено, падіння поспіль: ");
    (void)uart_sync_dec(dump->crash_count);
    (void)uart_sync_newline();

    // Перше, на що дивляться: PC — де саме зупинилося, LR — звідки прийшли.
    print_reg("PC ", dump->frame.pc);
    print_reg("LR ", dump->frame.lr);
    print_reg("PSR", dump->frame.psr);
    print_reg("R0 ", dump->frame.r0);
    print_reg("R1 ", dump->frame.r1);
    print_reg("R2 ", dump->frame.r2);
    print_reg("R3 ", dump->frame.r3);
    print_reg("R12", dump->frame.r12);

    (void)uart_sync_write("  стек аварії: ");
    (void)uart_sync_write((dump->exc_return & (1u << 2)) ? "PSP (код задачі)\r\n"
                                                        : "MSP (обробник або bare-metal)\r\n");

    print_reg("EXC_RETURN", dump->exc_return);
    print_reg("SHCSR", dump->shcsr);

    print_reg("HFSR", dump->hfsr);
    print_named_bits(dump->hfsr, k_hfsr_bits,
                     sizeof(k_hfsr_bits) / sizeof(k_hfsr_bits[0]));

    print_reg("CFSR", dump->cfsr);
    (void)uart_sync_write("    MemManage:\r\n");
    print_named_bits(dump->cfsr, k_mem_bits, sizeof(k_mem_bits) / sizeof(k_mem_bits[0]));
    (void)uart_sync_write("    BusFault:\r\n");
    print_named_bits(dump->cfsr, k_bus_bits, sizeof(k_bus_bits) / sizeof(k_bus_bits[0]));
    (void)uart_sync_write("    UsageFault:\r\n");
    print_named_bits(dump->cfsr, k_usage_bits,
                     sizeof(k_usage_bits) / sizeof(k_usage_bits[0]));

    // Адресні регістри мають сенс лише разом зі своїм бітом дійсності: без
    // нього там лежить адреса з якоїсь минулої, давно забутої помилки.
    if ((dump->cfsr & SCB_CFSR_MMARVALID_Msk) != 0u) {
        print_reg("MMFAR (адреса порушення MPU)", dump->mmfar);
    }
    if ((dump->cfsr & SCB_CFSR_BFARVALID_Msk) != 0u) {
        print_reg("BFAR (адреса помилки шини)", dump->bfar);
    }

    switch ((fpu_frame_state_t)dump->fpu_state) {
    case FPU_FRAME_NONE:
        (void)uart_sync_write("  FPU: базовий кадр, співпроцесор не задіяно\r\n");
        break;
    case FPU_FRAME_LAZY:
        (void)uart_sync_write("  FPU: розширений кадр, але S0-S15 ще не збережено (lazy)\r\n");
        break;
    case FPU_FRAME_SAVED:
        print_reg("FPSCR", dump->fpscr);
        for (int i = 0; i < 16; ++i) {
            (void)uart_sync_write("  S");
            (void)uart_sync_dec((uint32_t)i);
            (void)uart_sync_write(" = ");
            (void)uart_sync_hex32(dump->s[i]);
            (void)uart_sync_newline();
        }
        break;
    default:
        (void)uart_sync_write("  FPU: стан невідомий\r\n");
        break;
    }
}

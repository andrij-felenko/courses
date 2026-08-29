#include "fault.h"

#include "trace.h"
#include "stm32f4xx.h"

typedef struct {
    uint32_t    mask;
    const char *name;
} bit_name_t;

static const bit_name_t k_hfsr_bits[] = {
    { SCB_HFSR_DEBUGEVT_Msk, "DEBUGEVT подія налагодження (breakpoint/watchpoint)" },
    { SCB_HFSR_FORCED_Msk,   "FORCED   ескалація: справжня причина в CFSR" },
    { SCB_HFSR_VECTTBL_Msk,  "VECTTBL  помилка читання таблиці векторів (перевір VTOR)" }
};

static const bit_name_t k_mmfsr_bits[] = {
    { SCB_CFSR_IACCVIOL_Msk,  "IACCVIOL   вибірка коду з області XN" },
    { SCB_CFSR_DACCVIOL_Msk,  "DACCVIOL   заборонений доступ до даних (MPU)" },
    { SCB_CFSR_MUNSTKERR_Msk, "MUNSTKERR  збій зняття кадру зі стека" },
    { SCB_CFSR_MSTKERR_Msk,   "MSTKERR    збій укладання кадру — типове переповнення стека" },
    { SCB_CFSR_MLSPERR_Msk,   "MLSPERR    збій лінивого збереження регістрів FPU" }
};

static const bit_name_t k_bfsr_bits[] = {
    { SCB_CFSR_IBUSERR_Msk,     "IBUSERR      помилка шини при вибірці інструкції" },
    { SCB_CFSR_PRECISERR_Msk,   "PRECISERR    точна помилка шини — PC вказує на винну інструкцію" },
    { SCB_CFSR_IMPRECISERR_Msk, "IMPRECISERR  неточна помилка шини — PC зсунуто, дивись BFAR-и вручну" },
    { SCB_CFSR_UNSTKERR_Msk,    "UNSTKERR     збій шини при знятті кадру" },
    { SCB_CFSR_STKERR_Msk,      "STKERR       збій шини при укладанні кадру" },
    { SCB_CFSR_LSPERR_Msk,      "LSPERR       збій шини при збереженні регістрів FPU" }
};

static const bit_name_t k_ufsr_bits[] = {
    { SCB_CFSR_UNDEFINSTR_Msk, "UNDEFINSTR  невідомий опкод: перехід у дані або затертий стек" },
    { SCB_CFSR_INVSTATE_Msk,   "INVSTATE    втрачено біт Thumb: парна адреса переходу" },
    { SCB_CFSR_INVPC_Msk,      "INVPC       пошкоджений EXC_RETURN при виході з переривання" },
    { SCB_CFSR_NOCP_Msk,       "NOCP        інструкція FPU при вимкненому співпроцесорі (CPACR)" },
    { SCB_CFSR_UNALIGNED_Msk,  "UNALIGNED   невирівняний доступ" },
    { SCB_CFSR_DIVBYZERO_Msk,  "DIVBYZERO   ділення на нуль" }
};

static const char *const k_tag_names[] = {
    "HardFault", "MemManage", "BusFault", "UsageFault"
};

static void print_bits(const char *title, const bit_name_t *table, uint32_t count, uint32_t value)
{
    uint32_t printed = 0u;

    trace_str(title);
    trace_str(": ");
    trace_hex32(value);
    trace_str("\r\n");

    for (uint32_t i = 0u; i < count; ++i) {
        if ((value & table[i].mask) != 0u) {
            trace_str("    - ");
            trace_str(table[i].name);
            trace_str("\r\n");
            ++printed;
        }
    }
    if (printed == 0u) {
        trace_str("    - (жодного біта)\r\n");
    }
}

/*
 * Кадр беремо тільки з адреси, яка справді схожа на стек: вирівняна по слову
 * і лежить у SRAM або CCM. Якщо збій стався саме через зруйнований SP,
 * сліпе розіменування дало б другий збій усередині обробника — і Lockup.
 */
static int frame_is_readable(uint32_t sp)
{
    const uint32_t frame_size = (uint32_t)sizeof(cortex_frame_t);

    if ((sp & 0x3u) != 0u) {
        return 0;
    }
    if (sp >= 0x20000000u && (sp + frame_size) <= 0x20020000u) {
        return 1; /* основна SRAM STM32F407 */
    }
    if (sp >= 0x10000000u && (sp + frame_size) <= 0x10010000u) {
        return 1; /* CCM */
    }
    return 0;
}

static void print_exc_return(uint32_t exc_return)
{
    trace_kv("EXC_RETURN", exc_return);

    trace_str("    стек аварії: ");
    trace_str(((exc_return & 0x4u) != 0u) ? "PSP (задача RTOS)\r\n"
                                         : "MSP (головний стек або переривання)\r\n");

    trace_str("    режим до збою: ");
    trace_str(((exc_return & 0x8u) != 0u) ? "Thread\r\n" : "Handler (збій усередині переривання)\r\n");

    trace_str("    кадр FPU: ");
    trace_str(((exc_return & 0x10u) == 0u) ? "розширений (+18 слів S0-S15, FPSCR)\r\n"
                                           : "базовий (8 слів)\r\n");
}

static void print_hint(uint32_t cfsr)
{
    trace_str("підказка: ");

    if ((cfsr & (SCB_CFSR_MSTKERR_Msk | SCB_CFSR_UNDEFINSTR_Msk | SCB_CFSR_INVSTATE_Msk)) != 0u) {
        trace_str("перевір глибину стека й покажчики на функції\r\n");
    } else if ((cfsr & SCB_CFSR_IMPRECISERR_Msk) != 0u) {
        trace_str("звертання до периферії без тактування; повтори з DISDEFWBUF=1\r\n");
    } else if ((cfsr & SCB_CFSR_PRECISERR_Msk) != 0u) {
        trace_str("дивись BFAR: нульовий покажчик або чужа адреса\r\n");
    } else if ((cfsr & SCB_CFSR_DACCVIOL_Msk) != 0u) {
        trace_str("порушення прав MPU: перевір регіони й покажчики на NULL\r\n");
    } else if ((cfsr & SCB_CFSR_UNALIGNED_Msk) != 0u) {
        trace_str("невирівняне приведення буфера до покажчика на слово\r\n");
    } else if ((cfsr & SCB_CFSR_DIVBYZERO_Msk) != 0u) {
        trace_str("нульовий дільник у цілочисловому діленні\r\n");
    } else {
        trace_str("CFSR порожній — дивись HFSR.VECTTBL і цілість VTOR\r\n");
    }
}

void fault_report(uint32_t frame_sp, uint32_t exc_return, uint32_t tag)
{
    const uint32_t hfsr = SCB->HFSR;
    const uint32_t cfsr = SCB->CFSR;

    trace_str("\r\n!!! ");
    trace_str((tag < 4u) ? k_tag_names[tag] : "невідомий вектор");
    trace_str(" !!!\r\n");

    print_exc_return(exc_return);
    trace_kv("frame SP", frame_sp);

    if (frame_is_readable(frame_sp)) {
        const cortex_frame_t *frame = (const cortex_frame_t *)frame_sp;

        trace_kv("  R0 ", frame->r0);
        trace_kv("  R1 ", frame->r1);
        trace_kv("  R2 ", frame->r2);
        trace_kv("  R3 ", frame->r3);
        trace_kv("  R12", frame->r12);
        trace_kv("  LR ", frame->lr);
        trace_kv("  PC ", frame->pc);
        trace_kv("  PSR", frame->psr);

        /*
         * Номер активного винятку в момент аварії: 0 — код задачі,
         * інше — переривання з таблиці векторів.
         */
        trace_kv("  IPSR", frame->psr & 0x1FFu);

        trace_str("addr2line: arm-none-eabi-addr2line -e firmware.elf -f -C -a ");
        trace_hex32(frame->pc);
        trace_str("\r\n");
    } else {
        /* Сам SP зруйновано — це вже діагноз: переповнення стека або чужий запис. */
        trace_str("кадр недоступний: SP не вказує на RAM (переповнення стека?)\r\n");
    }

    print_bits("HFSR", k_hfsr_bits, sizeof(k_hfsr_bits) / sizeof(k_hfsr_bits[0]), hfsr);
    print_bits("MMFSR", k_mmfsr_bits, sizeof(k_mmfsr_bits) / sizeof(k_mmfsr_bits[0]), cfsr & 0xFFu);
    print_bits("BFSR", k_bfsr_bits, sizeof(k_bfsr_bits) / sizeof(k_bfsr_bits[0]), cfsr & 0xFF00u);
    print_bits("UFSR", k_ufsr_bits, sizeof(k_ufsr_bits) / sizeof(k_ufsr_bits[0]), cfsr & 0xFFFF0000u);

    if ((cfsr & SCB_CFSR_MMARVALID_Msk) != 0u) {
        trace_kv("MMFAR", SCB->MMFAR);
    } else {
        trace_str("MMFAR: недійсний (MMARVALID=0)\r\n");
    }

    if ((cfsr & SCB_CFSR_BFARVALID_Msk) != 0u) {
        trace_kv("BFAR ", SCB->BFAR);
    } else {
        trace_str("BFAR: недійсний (BFARVALID=0)\r\n");
    }

    print_hint(cfsr);

    /*
     * Прапорці статусу скидаються записом одиниці. Робимо це, щоб наступна
     * аварія не показала суміш зі старими бітами, якщо чип переживе цей збій.
     */
    SCB->HFSR = hfsr;
    SCB->CFSR = cfsr;
}

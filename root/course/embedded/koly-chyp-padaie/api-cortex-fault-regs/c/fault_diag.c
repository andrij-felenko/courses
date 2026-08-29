#include "fault_diag.h"
#include "diag_out.h"

#include "stm32f4xx.h"   /* CMSIS: SCB, SCnSCB, FPU, CoreDebug */

/* ---------------------------------------------------------------- таблиці */

static const struct diag_flag k_hfsr_flags[] = {
    { SCB_HFSR_DEBUGEVT_Msk, "DEBUGEVT", "збій підняв відладчик (breakpoint / DWT)" },
    { SCB_HFSR_FORCED_Msk,   "FORCED",   "ескалація підлеглого винятку — справжня причина в CFSR" },
    /* У CMSIS біт зветься VECTTBL, у довіднику ARM — VECTBL. */
    { SCB_HFSR_VECTTBL_Msk,  "VECTBL",   "не вдалося прочитати вектор: зіпсовано VTOR або таблицю" },
};

static const struct diag_flag k_mmfsr_flags[] = {
    { SCB_CFSR_MMARVALID_Msk, "MMARVALID", "адреса збою лежить у MMFAR" },
    { SCB_CFSR_MSTKERR_Msk,   "MSTKERR",   "MPU заборонив запис кадру при вході у виняток" },
    { SCB_CFSR_MUNSTKERR_Msk, "MUNSTKERR", "MPU заборонив читання кадру при виході з винятку" },
    { SCB_CFSR_DACCVIOL_Msk,  "DACCVIOL",  "доступ до даних поза дозволеним регіоном MPU" },
    { SCB_CFSR_IACCVIOL_Msk,  "IACCVIOL",  "вибірка коду з області XN або з дірки в карті пам'яті" },
};

static const struct diag_flag k_bfsr_flags[] = {
    { SCB_CFSR_BFARVALID_Msk,  "BFARVALID",  "адреса збою лежить у BFAR" },
    { SCB_CFSR_STKERR_Msk,     "STKERR",     "помилка шини при збереженні кадру винятку" },
    { SCB_CFSR_UNSTKERR_Msk,   "UNSTKERR",   "помилка шини при відновленні кадру" },
    { SCB_CFSR_IMPRECISERR_Msk,"IMPRECISERR","НЕточна помилка запису: PC у кадрі не вказує на винну інструкцію" },
    { SCB_CFSR_PRECISERR_Msk,  "PRECISERR",  "точна помилка даних: PC у кадрі — саме та інструкція" },
    { SCB_CFSR_IBUSERR_Msk,    "IBUSERR",    "помилка шини при вибірці інструкції" },
};

static const struct diag_flag k_ufsr_flags[] = {
    { SCB_CFSR_DIVBYZERO_Msk,  "DIVBYZERO",  "SDIV/UDIV з нульовим дільником" },
    { SCB_CFSR_UNALIGNED_Msk,  "UNALIGNED",  "невирівняний доступ (завжди для LDRD/STRD/LDM/STM)" },
    { SCB_CFSR_NOCP_Msk,       "NOCP",       "інструкція співпроцесора при закритому доступі — типово FPU без CPACR" },
    { SCB_CFSR_INVPC_Msk,      "INVPC",      "невалідний EXC_RETURN або PC при поверненні" },
    { SCB_CFSR_INVSTATE_Msk,   "INVSTATE",   "скинуто біт Thumb: стрибок за парною адресою чи на дані" },
    { SCB_CFSR_UNDEFINSTR_Msk, "UNDEFINSTR", "нерозпізнаний опкод: затерто код або стрибок у дані" },
};

static const char *source_name(uint32_t source)
{
    switch (source) {
    case FAULT_SOURCE_HARD:      return "HardFault";
    case FAULT_SOURCE_MEMMANAGE: return "MemManage";
    case FAULT_SOURCE_BUS:       return "BusFault";
    case FAULT_SOURCE_USAGE:     return "UsageFault";
    default:                     return "невідомий виняток";
    }
}

/* ------------------------------------------------------------ ініціалізація */

void fault_diag_init(void)
{
    /* 1. Роздільні обробники: без цих трьох бітів кожен MemManage, BusFault
     *    чи UsageFault одразу ескалює в HardFault із прапорцем FORCED. */
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk |
                  SCB_SHCSR_BUSFAULTENA_Msk |
                  SCB_SHCSR_USGFAULTENA_Msk;

    /* 2. Апаратні пастки: ділення на нуль і невирівняний доступ. Без DIV_0_TRP
     *    ділення на нуль тихо дає нуль, і помилка спливе далеко від місця. */
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk |
                SCB_CCR_UNALIGN_TRP_Msk |
                SCB_CCR_STKALIGN_Msk;   /* вимога AAPCS: кадр вирівняний на 8 */

#if defined(__FPU_PRESENT) && (__FPU_PRESENT == 1)
    /* 3. Доступ до співпроцесорів CP10/CP11 — повний (0b11 у кожне поле).
     *    Без цього перша ж інструкція VADD дасть UsageFault: NOCP. */
    SCB->CPACR |= (3UL << 20) | (3UL << 22);
    __DSB();
    __ISB();

    /* Автоматичне резервування кадру FPU плюс лінива його побудова: місце на
     * стеку виділяється завжди, а самі S0–S15 їдуть у пам'ять лише тоді, коли
     * обробник сам торкнеться FPU. */
    FPU->FPCCR |= FPU_FPCCR_ASPEN_Msk | FPU_FPCCR_LSPEN_Msk;
#endif

#ifdef DEBUG
    /* 4. Вимкнути буфер запису: усі помилки запису стають точними
     *    (PRECISERR + BFARVALID), тобто вкажуть на конкретний рядок коду.
     *    У CMSIS цей регістр лежить не в SCB, а в SCnSCB (0xE000E008). */
    SCnSCB->ACTLR |= SCnSCB_ACTLR_DISDEFWBUF_Msk;
#endif

    __DSB();
    __ISB();
}

/* ------------------------------------------------------------------ розбір */

/* Безпечне читання адреси зсередини HardFault.
 *
 * BFHFNMIGN діє лише на пріоритетах -1 і -2 (HardFault, NMI): помилка шини
 * там не породжує нового винятку й не заганяє ядро в Lockup — вона просто
 * ігнорується, а слід лишається в BFSR. Тому й перевіряємо результат по
 * PRECISERR, а не по значенню.
 */
static bool probe_read32(uint32_t address, uint32_t *out)
{
    /* Стираємо липкі сліди попередніх подій, щоб судити саме про це читання. */
    SCB->CFSR = SCB_CFSR_PRECISERR_Msk | SCB_CFSR_BFARVALID_Msk;

    const uint32_t saved_ccr = SCB->CCR;
    SCB->CCR = saved_ccr | SCB_CCR_BFHFNMIGN_Msk;
    __DSB();
    __ISB();

    const uint32_t value = *(const volatile uint32_t *)address;
    __DSB();

    SCB->CCR = saved_ccr;
    __DSB();
    __ISB();

    if ((SCB->CFSR & SCB_CFSR_PRECISERR_Msk) != 0u) {
        SCB->CFSR = SCB_CFSR_PRECISERR_Msk | SCB_CFSR_BFARVALID_Msk;
        return false;
    }

    *out = value;
    return true;
}

static void report_exc_return(uint32_t exc_return)
{
    diag_puts("Стан ядра до аварії (EXC_RETURN):\n");
    diag_reg("LR при вході", exc_return);

    diag_puts("    * режим: ");
    diag_puts((exc_return & (1u << 3)) != 0u
              ? "Thread — упала звичайна програма\n"
              : "Handler — упало ВСЕРЕДИНІ іншого переривання\n");

    diag_puts("    * стек кадру: ");
    diag_puts((exc_return & (1u << 2)) != 0u
              ? "PSP (стек задачі RTOS)\n"
              : "MSP (головний стек)\n");

    diag_puts("    * кадр: ");
    diag_puts((exc_return & (1u << 4)) != 0u
              ? "базовий, 8 слів\n"
              : "розширений із контекстом FPU, 26 слів\n");
}

static void report_frame(const struct exception_frame *frame)
{
    diag_puts("Кадр аварії:\n");
    diag_reg("R0 ", frame->r0);
    diag_reg("R1 ", frame->r1);
    diag_reg("R2 ", frame->r2);
    diag_reg("R3 ", frame->r3);
    diag_reg("R12", frame->r12);
    diag_reg("LR ", frame->lr);
    diag_reg("PC ", frame->pc);
    diag_reg("PSR", frame->psr);

    /* Молодші 9 бітів PSR — номер активного винятку; для коду в Thread Mode
     * там нуль. Це друга, незалежна від EXC_RETURN, відповідь на питання
     * «чи впали ми в перериванні». */
    const uint32_t ipsr = frame->psr & 0x1FFu;
    if (ipsr != 0u) {
        diag_puts("    * перерваний код сам був у винятку №");
        diag_u32(ipsr);
        diag_nl();
    }
}

static void report_fpu(uint32_t exc_return, const struct exception_frame *frame)
{
#if defined(__FPU_PRESENT) && (__FPU_PRESENT == 1)
    const uint32_t fpccr = FPU->FPCCR;
    diag_puts("FPU:\n");
    diag_reg("FPCCR", fpccr);

    if ((fpccr & FPU_FPCCR_LSPACT_Msk) != 0u) {
        diag_puts("    * LSPACT=1: місце під S0–S15 на стеку зарезервовано,\n"
                  "      але значення туди ще НЕ записані — читати їх звідти марно\n");
    } else if ((exc_return & (1u << 4)) == 0u) {
        /* Розширений кадр і ліниве збереження вже відпрацювало: за базовими
         * вісьмома словами лежать S0–S15, далі FPSCR. */
        const uint32_t *ext = (const uint32_t *)(frame + 1);
        diag_reg("S0   ", ext[0]);
        diag_reg("S1   ", ext[1]);
        diag_reg("FPSCR", ext[16]);
    }
#else
    (void)exc_return;
    (void)frame;
#endif
}

static void report_code_at_pc(uint32_t pc)
{
    /* PC у кадрі може вказувати куди завгодно — саме тому читаємо через
     * probe_read32, а не напряму. Вирівнюємо на слово: Thumb-інструкція
     * буває на півслові. */
    const uint32_t base = pc & ~3u;
    uint32_t word = 0;

    diag_puts("Пам'ять навколо PC:\n");
    for (int i = -1; i <= 1; ++i) {
        const uint32_t addr = base + (uint32_t)(i * 4);
        diag_puts("    ");
        diag_hex32(addr);
        diag_puts(" : ");
        if (probe_read32(addr, &word)) {
            diag_hex32(word);
        } else {
            diag_puts("недоступна (помилка шини)");
        }
        diag_nl();
    }
}

/* --------------------------------------------------------------- завершення */

static void halt_or_reset(void)
{
    /* Під відладчиком зупиняємось на місці: увесь контекст ще живий і його
     * можна колупати руками. Без відладчика зависати не можна — виріб
     * має піднятися, тому перезапускаємось. */
    if ((CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0u) {
        __BKPT(0);
    }

    NVIC_SystemReset();

    /* NVIC_SystemReset() не повертається, але компілятор про це не знає. */
    for (;;) {
    }
}

void fault_report_entry(const struct exception_frame *frame,
                        uint32_t exc_return,
                        uint32_t source)
{
    const uint32_t hfsr = SCB->HFSR;
    const uint32_t cfsr = SCB->CFSR;
    const uint32_t mmfar = SCB->MMFAR;
    const uint32_t bfar = SCB->BFAR;

    diag_puts("\n=== ЗБІЙ: ");
    diag_puts(source_name(source));
    diag_puts(" ===\n");

    /* HFSR */
    diag_puts("SCB->HFSR:\n");
    diag_reg("HFSR", hfsr);
    (void)diag_flags(k_hfsr_flags, sizeof k_hfsr_flags / sizeof k_hfsr_flags[0], hfsr);

    /* CFSR трьома шматками: CMSIS дає лише 32-бітне слово, байти вирізаємо самі. */
    diag_puts("SCB->CFSR:\n");
    diag_reg("CFSR ", cfsr);
    diag_reg("MMFSR", (cfsr >> 0) & 0xFFu);
    diag_reg("BFSR ", (cfsr >> 8) & 0xFFu);
    diag_reg("UFSR ", (cfsr >> 16) & 0xFFFFu);

    size_t named = 0;
    named += diag_flags(k_mmfsr_flags, sizeof k_mmfsr_flags / sizeof k_mmfsr_flags[0], cfsr);
    named += diag_flags(k_bfsr_flags, sizeof k_bfsr_flags / sizeof k_bfsr_flags[0], cfsr);
    named += diag_flags(k_ufsr_flags, sizeof k_ufsr_flags / sizeof k_ufsr_flags[0], cfsr);
    if (named == 0u) {
        /* Порожній CFSR при HardFault означає, що підлеглого збою не було:
         * дивись VECTBL і DEBUGEVT у HFSR. */
        diag_puts("    * CFSR порожній: підлеглого збою не зафіксовано\n");
    }

    /* Адресні регістри — лише під своїм прапорцем валідності. Читати їх без
     * перевірки означає читати сміття від попередніх аварій. */
    diag_puts("Адреси збою:\n");
    if ((cfsr & SCB_CFSR_MMARVALID_Msk) != 0u) {
        diag_reg("MMFAR", mmfar);
    } else {
        diag_puts("    MMFAR недійсний (MMARVALID=0)\n");
    }
    if ((cfsr & SCB_CFSR_BFARVALID_Msk) != 0u) {
        diag_reg("BFAR ", bfar);
    } else {
        diag_puts("    BFAR недійсний (BFARVALID=0)\n");
    }
    if ((cfsr & SCB_CFSR_IMPRECISERR_Msk) != 0u) {
        diag_puts("    УВАГА: помилка неточна — винний запис пішов через буфер,\n"
                  "    PC у кадрі вже втік уперед. Вимкни буфер (DISDEFWBUF)\n"
                  "    і повтори прогін, щоб дістати точну адресу.\n");
    }

    report_exc_return(exc_return);
    report_frame(frame);
    report_fpu(exc_return, frame);

    /* Зондувати пам'ять безпечно тільки з HardFault: BFHFNMIGN на пріоритетах
     * налаштовуваних обробників не діє, і помилка шини там ескалює в HardFault
     * замість того, щоб тихо загубитись. */
    if (source == FAULT_SOURCE_HARD) {
        report_code_at_pc(frame->pc);
    }

    /* Стираємо липкі прапорці (rc_w1), щоб наступна аварія показала свою
     * причину, а не суміш із цією. */
    SCB->HFSR = hfsr;
    SCB->CFSR = cfsr;
    __DSB();

    diag_puts("=== кінець звіту ===\n");
    halt_or_reset();
}

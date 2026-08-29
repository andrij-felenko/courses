#include "fault_report.hpp"

#include "trace.hpp"

#include "stm32f4xx.h"  // CMSIS: SCB, SCnSCB, FPU, CoreDebug

#include <array>

namespace fault {
namespace {

constexpr std::array k_hfsr_flags = std::to_array<trace::Flag>({
    { SCB_HFSR_DEBUGEVT_Msk, "DEBUGEVT", "збій підняв відладчик (breakpoint / DWT)" },
    { SCB_HFSR_FORCED_Msk,   "FORCED",   "ескалація підлеглого винятку — справжня причина в CFSR" },
    // У CMSIS біт зветься VECTTBL, у довіднику ARM — VECTBL.
    { SCB_HFSR_VECTTBL_Msk,  "VECTBL",   "не вдалося прочитати вектор: зіпсовано VTOR або таблицю" },
});

constexpr std::array k_mmfsr_flags = std::to_array<trace::Flag>({
    { SCB_CFSR_MMARVALID_Msk, "MMARVALID", "адреса збою лежить у MMFAR" },
    { SCB_CFSR_MSTKERR_Msk,   "MSTKERR",   "MPU заборонив запис кадру при вході у виняток" },
    { SCB_CFSR_MUNSTKERR_Msk, "MUNSTKERR", "MPU заборонив читання кадру при виході з винятку" },
    { SCB_CFSR_DACCVIOL_Msk,  "DACCVIOL",  "доступ до даних поза дозволеним регіоном MPU" },
    { SCB_CFSR_IACCVIOL_Msk,  "IACCVIOL",  "вибірка коду з області XN або з дірки в карті пам'яті" },
});

constexpr std::array k_bfsr_flags = std::to_array<trace::Flag>({
    { SCB_CFSR_BFARVALID_Msk,   "BFARVALID",   "адреса збою лежить у BFAR" },
    { SCB_CFSR_STKERR_Msk,      "STKERR",      "помилка шини при збереженні кадру винятку" },
    { SCB_CFSR_UNSTKERR_Msk,    "UNSTKERR",    "помилка шини при відновленні кадру" },
    { SCB_CFSR_IMPRECISERR_Msk, "IMPRECISERR", "НЕточна помилка запису: PC у кадрі не вказує на винну інструкцію" },
    { SCB_CFSR_PRECISERR_Msk,   "PRECISERR",   "точна помилка даних: PC у кадрі — саме та інструкція" },
    { SCB_CFSR_IBUSERR_Msk,     "IBUSERR",     "помилка шини при вибірці інструкції" },
});

constexpr std::array k_ufsr_flags = std::to_array<trace::Flag>({
    { SCB_CFSR_DIVBYZERO_Msk,  "DIVBYZERO",  "SDIV/UDIV з нульовим дільником" },
    { SCB_CFSR_UNALIGNED_Msk,  "UNALIGNED",  "невирівняний доступ (завжди для LDRD/STRD/LDM/STM)" },
    { SCB_CFSR_NOCP_Msk,       "NOCP",       "інструкція співпроцесора при закритому доступі — типово FPU без CPACR" },
    { SCB_CFSR_INVPC_Msk,      "INVPC",      "невалідний EXC_RETURN або PC при поверненні" },
    { SCB_CFSR_INVSTATE_Msk,   "INVSTATE",   "скинуто біт Thumb: стрибок за парною адресою чи на дані" },
    { SCB_CFSR_UNDEFINSTR_Msk, "UNDEFINSTR", "нерозпізнаний опкод: затерто код або стрибок у дані" },
});

constexpr std::string_view source_name(Source source)
{
    switch (source) {
    case Source::hard:       return "HardFault";
    case Source::mem_manage: return "MemManage";
    case Source::bus:        return "BusFault";
    case Source::usage:      return "UsageFault";
    }
    return "невідомий виняток";
}

void report_exc_return(ExcReturn lr)
{
    trace::out() << "Стан ядра до аварії (EXC_RETURN):\n";
    trace::reg("LR при вході", lr.raw());

    trace::out() << "    * режим: "
                 << (lr.from_thread() ? "Thread — упала звичайна програма\n"
                                      : "Handler — упало ВСЕРЕДИНІ іншого переривання\n");

    trace::out() << "    * стек кадру: "
                 << (lr.uses_process_stack() ? "PSP (стек задачі RTOS)\n"
                                             : "MSP (головний стек)\n");

    trace::out() << "    * кадр: "
                 << (lr.basic_frame() ? "базовий, 8 слів\n"
                                      : "розширений із контекстом FPU, 26 слів\n");
}

void report_frame(const ExceptionFrame& frame)
{
    trace::out() << "Кадр аварії:\n";
    trace::reg("R0 ", frame.r0);
    trace::reg("R1 ", frame.r1);
    trace::reg("R2 ", frame.r2);
    trace::reg("R3 ", frame.r3);
    trace::reg("R12", frame.r12);
    trace::reg("LR ", frame.lr);
    trace::reg("PC ", frame.pc);
    trace::reg("PSR", frame.psr);

    // Молодші 9 бітів PSR — номер активного винятку. Це друга, незалежна від
    // EXC_RETURN, відповідь на питання «чи впали ми в перериванні».
    if (const std::uint32_t ipsr = frame.psr & 0x1FFu; ipsr != 0u) {
        trace::out() << "    * перерваний код сам був у винятку №" << ipsr << '\n';
    }
}

void report_fpu(ExcReturn lr, const ExceptionFrame& frame)
{
#if defined(__FPU_PRESENT) && (__FPU_PRESENT == 1)
    const std::uint32_t fpccr = FPU->FPCCR;

    trace::out() << "FPU:\n";
    trace::reg("FPCCR", fpccr);

    if ((fpccr & FPU_FPCCR_LSPACT_Msk) != 0u) {
        trace::out() << "    * LSPACT=1: місце під S0–S15 на стеку зарезервовано,\n"
                        "      але значення туди ще НЕ записані — читати їх звідти марно\n";
    } else if (!lr.basic_frame()) {
        // Розширений кадр, і ліниве збереження вже відпрацювало: за базовими
        // вісьмома словами лежать S0–S15, далі FPSCR.
        const auto* extended = reinterpret_cast<const std::uint32_t*>(&frame + 1);
        trace::reg("S0   ", extended[0]);
        trace::reg("S1   ", extended[1]);
        trace::reg("FPSCR", extended[16]);
    }
#else
    static_cast<void>(lr);
    static_cast<void>(frame);
#endif
}

void report_code_at_pc(std::uint32_t pc, Source source)
{
    // PC у кадрі може вказувати куди завгодно — саме тому читаємо через
    // probe_read. Вирівнюємо на слово: Thumb-інструкція буває на півслові.
    const std::uint32_t base = pc & ~3u;

    trace::out() << "Пам'ять навколо PC:\n";
    for (int offset = -1; offset <= 1; ++offset) {
        const auto address = static_cast<std::uint32_t>(base + offset * 4);

        trace::out() << "    " << trace::Hex{address} << " : ";
        if (const auto word = probe_read(address, source); word.has_value()) {
            trace::out() << trace::Hex{*word};
        } else {
            trace::out() << (word.error() == ProbeError::bus_error
                             ? "недоступна (помилка шини)"
                             : "не зондували: небезпечний контекст");
        }
        trace::out() << '\n';
    }
}

[[noreturn]] void halt_or_reset()
{
    // Під відладчиком зупиняємось на місці: увесь контекст ще живий і його
    // можна колупати руками. Без відладчика зависати не можна — виріб має
    // піднятися, тому перезапускаємось.
    if ((CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0u) {
        __BKPT(0);
    }

    NVIC_SystemReset();

    for (;;) {  // NVIC_SystemReset() не повертається, але компілятор про це не знає
    }
}

}  // namespace

std::optional<std::uint32_t> mem_fault_address()
{
    if ((SCB->CFSR & SCB_CFSR_MMARVALID_Msk) == 0u) {
        return std::nullopt;
    }
    return SCB->MMFAR;
}

std::optional<std::uint32_t> bus_fault_address()
{
    if ((SCB->CFSR & SCB_CFSR_BFARVALID_Msk) == 0u) {
        return std::nullopt;
    }
    return SCB->BFAR;
}

std::expected<std::uint32_t, ProbeError> probe_read(std::uintptr_t address, Source source)
{
    // BFHFNMIGN діє лише на пріоритетах -1 і -2 (HardFault, NMI): помилка шини
    // там не породжує нового винятку й не заганяє ядро в Lockup. У звичайному
    // обробнику вона, навпаки, ескалює — і ми втратимо звіт, який уже пишемо.
    if (source != Source::hard) {
        return std::unexpected(ProbeError::unsafe_context);
    }

    constexpr std::uint32_t bus_marks = SCB_CFSR_PRECISERR_Msk | SCB_CFSR_BFARVALID_Msk;

    // Стираємо липкі сліди попередніх подій, щоб судити саме про це читання.
    SCB->CFSR = bus_marks;

    const std::uint32_t saved_ccr = SCB->CCR;
    SCB->CCR = saved_ccr | SCB_CCR_BFHFNMIGN_Msk;
    __DSB();
    __ISB();

    const std::uint32_t value = *reinterpret_cast<const volatile std::uint32_t*>(address);
    __DSB();

    SCB->CCR = saved_ccr;
    __DSB();
    __ISB();

    // Значення могли й не прочитати: помилку шини просто проігнорували,
    // а слід лишився в BFSR — тому судимо по прапорцю, не по вмісту.
    if ((SCB->CFSR & SCB_CFSR_PRECISERR_Msk) != 0u) {
        SCB->CFSR = bus_marks;
        return std::unexpected(ProbeError::bus_error);
    }

    return value;
}

void init_diagnostics() noexcept
{
    // 1. Роздільні обробники: без цих трьох бітів кожен MemManage, BusFault
    //    чи UsageFault одразу ескалює в HardFault із прапорцем FORCED.
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk |
                  SCB_SHCSR_BUSFAULTENA_Msk |
                  SCB_SHCSR_USGFAULTENA_Msk;

    // 2. Апаратні пастки: ділення на нуль і невирівняний доступ. Без DIV_0_TRP
    //    ділення на нуль тихо дає нуль, і помилка спливе далеко від місця.
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk |
                SCB_CCR_UNALIGN_TRP_Msk |
                SCB_CCR_STKALIGN_Msk;   // вимога AAPCS: кадр вирівняний на 8

#if defined(__FPU_PRESENT) && (__FPU_PRESENT == 1)
    // 3. Доступ до співпроцесорів CP10/CP11 — повний (0b11 у кожне поле).
    //    Без цього перша ж інструкція VADD дасть UsageFault: NOCP.
    SCB->CPACR |= (3UL << 20) | (3UL << 22);
    __DSB();
    __ISB();

    // Автоматичне резервування кадру FPU плюс лінива його побудова: місце на
    // стеку виділяється завжди, а самі S0–S15 їдуть у пам'ять лише тоді, коли
    // обробник сам торкнеться FPU.
    FPU->FPCCR |= FPU_FPCCR_ASPEN_Msk | FPU_FPCCR_LSPEN_Msk;
#endif

#ifdef DEBUG
    // 4. Вимкнути буфер запису: усі помилки запису стають точними
    //    (PRECISERR + BFARVALID), тобто вкажуть на конкретний рядок коду.
    //    У CMSIS цей регістр лежить не в SCB, а в SCnSCB (0xE000E008).
    SCnSCB->ACTLR |= SCnSCB_ACTLR_DISDEFWBUF_Msk;
#endif

    __DSB();
    __ISB();
}

void report(const ExceptionFrame& frame, ExcReturn lr, Source source)
{
    const std::uint32_t hfsr = SCB->HFSR;
    const std::uint32_t cfsr = SCB->CFSR;

    // Адреси знімаємо ДО очищення CFSR: без прапорців валідності вони
    // перетворяться на сміття.
    const auto mm_address = mem_fault_address();
    const auto bus_address = bus_fault_address();

    trace::out() << "\n=== ЗБІЙ: " << source_name(source) << " ===\n";

    trace::out() << "SCB->HFSR:\n";
    trace::reg("HFSR", hfsr);
    trace::print_flags(k_hfsr_flags, hfsr);

    // CFSR трьома шматками: CMSIS дає лише 32-бітне слово, байти вирізаємо самі.
    trace::out() << "SCB->CFSR:\n";
    trace::reg("CFSR ", cfsr);
    trace::reg("MMFSR", (cfsr >> 0) & 0xFFu);
    trace::reg("BFSR ", (cfsr >> 8) & 0xFFu);
    trace::reg("UFSR ", (cfsr >> 16) & 0xFFFFu);

    std::size_t named = 0;
    named += trace::print_flags(k_mmfsr_flags, cfsr);
    named += trace::print_flags(k_bfsr_flags, cfsr);
    named += trace::print_flags(k_ufsr_flags, cfsr);
    if (named == 0) {
        // Порожній CFSR при HardFault означає, що підлеглого збою не було:
        // дивись VECTBL і DEBUGEVT у HFSR.
        trace::out() << "    * CFSR порожній: підлеглого збою не зафіксовано\n";
    }

    trace::out() << "Адреси збою:\n";
    if (mm_address) {
        trace::reg("MMFAR", *mm_address);
    } else {
        trace::out() << "    MMFAR недійсний (MMARVALID=0)\n";
    }
    if (bus_address) {
        trace::reg("BFAR ", *bus_address);
    } else {
        trace::out() << "    BFAR недійсний (BFARVALID=0)\n";
    }
    if ((cfsr & SCB_CFSR_IMPRECISERR_Msk) != 0u) {
        trace::out() << "    УВАГА: помилка неточна — винний запис пішов через буфер,\n"
                        "    PC у кадрі вже втік уперед. Вимкни буфер (DISDEFWBUF)\n"
                        "    і повтори прогін, щоб дістати точну адресу.\n";
    }

    report_exc_return(lr);
    report_frame(frame);
    report_fpu(lr, frame);
    report_code_at_pc(frame.pc, source);

    // Стираємо липкі прапорці (rc_w1), щоб наступна аварія показала свою
    // причину, а не суміш із цією.
    SCB->HFSR = hfsr;
    SCB->CFSR = cfsr;
    __DSB();

    trace::out() << "=== кінець звіту ===\n";
    halt_or_reset();
}

}  // namespace fault

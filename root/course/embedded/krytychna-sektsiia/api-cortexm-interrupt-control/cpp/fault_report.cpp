#include "fault_report.hpp"

#include <array>
#include <type_traits>

namespace cortexm {
namespace {

constexpr std::uint32_t kMagic = 0x464C5421U;   /* 'FLT!' */

struct Slot {
    std::uint32_t magic;
    FaultRecord body;
};

/*
 * Запис мусить пережити програмне скидання, тому лежить у секції, яку
 * стартовий код НЕ чистить. У типовому скрипті лінкера для STM32 вона зветься
 * .noinit; якщо її в проєкті немає, її треба додати поруч із .bss — інакше
 * увесь цей модуль безглуздий.
 *
 * Змінна навмисно без ініціалізатора: будь-який ініціалізатор перетворив би
 * її на об'єкт із динамічною чи статичною ініціалізацією, і запис затерло б
 * саме на старті, коли ми його читаємо.
 */
[[gnu::section(".noinit")]] Slot g_slot;

static_assert(std::is_trivially_default_constructible_v<Slot>,
              "Запис у .noinit не сміє мати ініціалізації — інакше він не переживе скидання");
static_assert(std::is_trivially_copyable_v<FaultRecord>,
              "Запис копіюється в optional як байти");

/* Силовий каскад гасимо ПЕРШОЮ дією обробника, ще до будь-якого розбору:
 * шпаруватість лишилася такою, якою її поставив останній прохід контуру, і
 * кожен зайвий такт з нею — це струм в обмотці без керування. */
void kill_power_stage() noexcept
{
    TIM1->BDTR &= ~TIM_BDTR_MOE;   /* Main Output Enable геть: виходи у Z */
    regs::dsb();
}

#if !defined(__ARM_ARCH_6M__)

struct CauseEntry {
    std::uint32_t mask;
    std::string_view text;
};

/*
 * Порядок у таблиці — це порядок розбору. Одночасно встановлених бітів буває
 * кілька (наприклад, MSTKERR разом із DACCVIOL), і першим має стояти той, що
 * називає ПЕРВИННУ причину, а не наслідок.
 */
constexpr std::array<CauseEntry, 15> kCfsrCauses{{
    /* MemManage: права доступу, які роздав MPU. */
    { SCB_CFSR_IACCVIOL_Msk,    "MPU: вибірка інструкції із забороненої області" },
    { SCB_CFSR_DACCVIOL_Msk,    "MPU: доступ до даних без прав" },
    { SCB_CFSR_MSTKERR_Msk,     "MPU: складання кадру виключення на стек" },
    { SCB_CFSR_MUNSTKERR_Msk,   "MPU: зняття кадру виключення зі стека" },

    /* BusFault: шина відповіла помилкою або не відповіла зовсім. */
    { SCB_CFSR_IBUSERR_Msk,     "шина: вибірка інструкції за недійсною адресою" },
    { SCB_CFSR_PRECISERR_Msk,   "шина: точна помилка доступу — адреса в BFAR" },
    /*
     * Неточна помилка — прямий наслідок буфера запису: STR устиг «завершитися»
     * для конвеєра, ядро пішло далі, і лише потім шина сказала «ні». Ані BFAR,
     * ані PC у кадрі на винуватця вже не показують. Саме від цього рятує DSB
     * перед зміною маски.
     */
    { SCB_CFSR_IMPRECISERR_Msk, "шина: неточна помилка — запис завис у буфері" },
    { SCB_CFSR_STKERR_Msk,      "шина: складання кадру виключення на стек" },
    { SCB_CFSR_UNSTKERR_Msk,    "шина: зняття кадру виключення зі стека" },

    /* UsageFault: програма зробила те, чого архітектура не дозволяє. */
    { SCB_CFSR_DIVBYZERO_Msk,   "ділення на нуль (увімкнено CCR.DIV_0_TRP)" },
    { SCB_CFSR_UNALIGNED_Msk,   "невирівняний доступ до пам'яті" },
    { SCB_CFSR_NOCP_Msk,        "звернення до вимкненого співпроцесора (FPU?)" },
    { SCB_CFSR_INVPC_Msk,       "недійсний EXC_RETURN або PC при поверненні" },
    { SCB_CFSR_INVSTATE_Msk,    "перехід в ARM-стан: біт T у xPSR скинуто" },
    { SCB_CFSR_UNDEFINSTR_Msk,  "невизначена інструкція" }
}};

#endif /* !__ARM_ARCH_6M__ */

/* Стан масок читаємо першим ділом: вхід у виключення їх не міняє, тож тут ще
 * видно рівно те, у чому програма була, коли помилилася. */
[[nodiscard]] MaskSnapshot capture_masks() noexcept
{
    MaskSnapshot snapshot{};
    snapshot.primask = regs::read_primask();
#if !defined(__ARM_ARCH_6M__)
    snapshot.faultmask = regs::read_faultmask();
    snapshot.basepri = regs::read_basepri();
#else
    snapshot.faultmask = regs::FaultmaskState::Enabled;   /* регістра немає */
    snapshot.basepri = 0U;
#endif
    return snapshot;
}

}  // namespace

std::string_view to_string(FaultKind kind) noexcept
{
    switch (kind) {
    case FaultKind::Hard:      return "HardFault";
    case FaultKind::MemManage: return "MemManage";
    case FaultKind::Bus:       return "BusFault";
    case FaultKind::Usage:     return "UsageFault";
    }
    return "невідоме виключення";
}

bool FaultRecord::escalated() const noexcept
{
#if !defined(__ARM_ARCH_6M__)
    return (hfsr & SCB_HFSR_FORCED_Msk) != 0U;
#else
    /* На ARMv6-M настроюваних обробників немає взагалі: усе, що на M4 стало б
     * BusFault-ом, там одразу приходить HardFault-ом. Ескалація — не подія, а
     * єдиний можливий режим. */
    return true;
#endif
}

std::optional<std::uint32_t> FaultRecord::fault_address() const noexcept
{
    if (mmfar_valid) {
        return mmfar;
    }
    if (bfar_valid) {
        return bfar;
    }
    return std::nullopt;
}

std::string_view FaultRecord::cause() const noexcept
{
#if !defined(__ARM_ARCH_6M__)
    if ((hfsr & SCB_HFSR_VECTTBL_Msk) != 0U) {
        return "помилка читання таблиці векторів";
    }
    for (const CauseEntry& entry : kCfsrCauses) {
        if ((cfsr & entry.mask) != 0U) {
            return entry.text;
        }
    }
    if ((hfsr & SCB_HFSR_DEBUGEVT_Msk) != 0U) {
        return "подія зневадження без підключеного зневадника";
    }
#endif
    return "HardFault без ознак у регістрах стану";
}

std::optional<FaultRecord> take_last_fault() noexcept
{
    if (g_slot.magic != kMagic) {
        return std::nullopt;
    }
    const FaultRecord copy = g_slot.body;
    g_slot.magic = 0U;      /* один збій розбирається рівно один раз */
    regs::dsb();
    return copy;
}

void enable_configurable_faults() noexcept
{
#if !defined(__ARM_ARCH_6M__)
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk
                | SCB_SHCSR_BUSFAULTENA_Msk
                | SCB_SHCSR_USGFAULTENA_Msk;

    /* Ділення на нуль за замовчуванням мовчки дає нуль. Пастка робить із нього
     * UsageFault — саме той, який усередині секції стане HardFault-ом. */
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk;

    regs::dsb();
    regs::isb();
#endif
}

}  // namespace cortexm

extern "C" void fault_entry_to_c(const cortexm::ExceptionFrame* frame,
                                 std::uint32_t exc_return,
                                 std::uint32_t kind)
{
    using namespace cortexm;

    kill_power_stage();

    FaultRecord& rec = g_slot.body;
    rec.masks = capture_masks();
    rec.kind = static_cast<FaultKind>(kind);
    rec.exc_return = exc_return;
    rec.frame = *frame;

#if !defined(__ARM_ARCH_6M__)
    rec.hfsr = SCB->HFSR;
    rec.cfsr = SCB->CFSR;
    rec.mmfar_valid = (rec.cfsr & SCB_CFSR_MMARVALID_Msk) != 0U;
    rec.bfar_valid = (rec.cfsr & SCB_CFSR_BFARVALID_Msk) != 0U;
    rec.mmfar = rec.mmfar_valid ? SCB->MMFAR : 0U;
    rec.bfar = rec.bfar_valid ? SCB->BFAR : 0U;

    /* Прапорці липкі — знімаємо їх записом одиниці, щоб наступна аварія не
     * читалася поверх цієї. */
    SCB->HFSR = rec.hfsr;
    SCB->CFSR = rec.cfsr;
#else
    rec.hfsr = 0U;
    rec.cfsr = 0U;
    rec.mmfar_valid = false;
    rec.bfar_valid = false;
    rec.mmfar = 0U;
    rec.bfar = 0U;
#endif

    /* Печатку ставимо ОСТАННЬОЮ: обірваний запис не має вважатися дійсним. */
    regs::dsb();
    g_slot.magic = kMagic;
    regs::dsb();

    NVIC_SystemReset();
}

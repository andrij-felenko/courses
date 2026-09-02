#include "fault_report.h"

#include "cortexm_mask.h"

/*
 * Запис мусить пережити програмне скидання, тому лежить у секції, яку
 * стартовий код НЕ чистить. У типовому скрипті лінкера для STM32 така секція
 * зветься .noinit; якщо її в проєкті немає, її треба додати поруч із .bss,
 * інакше все нижче безглузде — startup обнулить запис до першого рядка main().
 */
#define FAULT_MAGIC 0x464C5421UL   /* 'FLT!' — ознака, що в RAM саме наш запис */

static struct {
    uint32_t magic;
    fault_record_t body;
} g_slot __attribute__((section(".noinit")));

/*
 * Силовий каскад гасимо ПЕРШОЮ дією обробника, ще до будь-якого розбору.
 * Причина проста: у момент помилки шпаруватість лишилася такою, якою її
 * поставив останній прохід контуру струму, і кожен зайвий такт з нею —
 * це струм в обмотці без жодного керування.
 */
static void kill_power_stage(void)
{
    TIM1->BDTR &= ~TIM_BDTR_MOE;   /* Main Output Enable геть: виходи у Z */
    __DSB();
}

void fault_entry_to_c(const fault_frame_t *frame, uint32_t exc_return, uint32_t kind)
{
    kill_power_stage();

    fault_record_t *rec = &g_slot.body;

    /*
     * Маски читаємо одразу. Вхід у виключення не міняє ані PRIMASK, ані
     * BASEPRI, ані FAULTMASK — тож тут ще видно рівно той стан, у якому
     * програма була, коли помилилася. Пізніше, після наших власних викликів,
     * ця інформація вже нічого не варта.
     */
    rec->primask = __get_PRIMASK();
#if !defined(__ARM_ARCH_6M__)
    rec->basepri = __get_BASEPRI();
    rec->faultmask = __get_FAULTMASK();
#else
    rec->basepri = 0U;     /* ARMv6-M цих регістрів не має */
    rec->faultmask = 0U;
#endif

    rec->kind = (fault_kind_t)kind;
    rec->exc_return = exc_return;
    rec->frame = *frame;

#if !defined(__ARM_ARCH_6M__)
    rec->hfsr = SCB->HFSR;
    rec->cfsr = SCB->CFSR;

    /*
     * FORCED — це і є ескалація: настроюваний обробник був заблокований або
     * вимкнений, і ядро підняло помилку до HardFault, якого не тримає ані
     * PRIMASK, ані BASEPRI.
     */
    rec->escalated = (rec->hfsr & SCB_HFSR_FORCED_Msk) != 0U;

    rec->mmfar_valid = (rec->cfsr & SCB_CFSR_MMARVALID_Msk) != 0U;
    rec->bfar_valid = (rec->cfsr & SCB_CFSR_BFARVALID_Msk) != 0U;
    rec->mmfar = rec->mmfar_valid ? SCB->MMFAR : 0U;
    rec->bfar = rec->bfar_valid ? SCB->BFAR : 0U;

    /* Прапорці липкі — знімаємо їх записом одиниці, щоб наступна аварія
     * не читалася поверх цієї. */
    SCB->HFSR = rec->hfsr;
    SCB->CFSR = rec->cfsr;
#else
    rec->hfsr = 0U;
    rec->cfsr = 0U;
    rec->mmfar_valid = false;
    rec->bfar_valid = false;
    rec->mmfar = 0U;
    rec->bfar = 0U;
    rec->escalated = true;   /* на ARMv6-M інших помилок і не буває */
#endif

    /* Печатку ставимо ОСТАННЬОЮ: обірваний запис не має вважатися дійсним. */
    __DSB();
    g_slot.magic = FAULT_MAGIC;
    __DSB();

    NVIC_SystemReset();
}

void fault_report_enable_configurable_faults(void)
{
#if !defined(__ARM_ARCH_6M__)
    SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk
                | SCB_SHCSR_BUSFAULTENA_Msk
                | SCB_SHCSR_USGFAULTENA_Msk;

    /* Ділення на нуль за замовчуванням мовчки дає нуль. Пастка робить із
     * нього UsageFault — саме той, який усередині секції стане HardFault-ом. */
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk;

    __DSB();
    __ISB();
#endif
}

const fault_record_t *fault_report_last(void)
{
    return (g_slot.magic == FAULT_MAGIC) ? &g_slot.body : NULL;
}

void fault_report_clear(void)
{
    g_slot.magic = 0U;
    __DSB();
}

bool fault_report_masked_at_fault(const fault_record_t *rec)
{
    if (rec == NULL) {
        return false;
    }
    /*
     * BASEPRI враховуємо нарівні з PRIMASK: поріг маскує й настроювані
     * обробники помилок, якщо їхній пріоритет чисельно не менший за поріг.
     * FAULTMASK тут може бути лише нулем — під ним обробник не запустився б.
     */
    return (rec->primask != 0U) || (rec->faultmask != 0U) || (rec->basepri != 0U);
}

bool fault_report_data_address(const fault_record_t *rec, uint32_t *out_address)
{
    if ((rec == NULL) || (out_address == NULL)) {
        return false;
    }
    if (rec->mmfar_valid) {
        *out_address = rec->mmfar;
        return true;
    }
    if (rec->bfar_valid) {
        *out_address = rec->bfar;
        return true;
    }
    return false;
}

/* ---- Розбір CFSR ------------------------------------------------------- */

#if !defined(__ARM_ARCH_6M__)

/*
 * Порядок у таблиці — це порядок розбору. Одночасно встановлених бітів буває
 * кілька (наприклад, MSTKERR разом із DACCVIOL), і першим має стояти той, що
 * називає ПЕРВИННУ причину, а не наслідок.
 */
static const struct {
    uint32_t mask;
    const char *text;
} k_cfsr_causes[] = {
    /* MemManage: права доступу, які роздав MPU. */
    { SCB_CFSR_IACCVIOL_Msk,   "MPU: вибірка інструкції із забороненої області" },
    { SCB_CFSR_DACCVIOL_Msk,   "MPU: доступ до даних без прав" },
    { SCB_CFSR_MSTKERR_Msk,    "MPU: складання кадру виключення на стек" },
    { SCB_CFSR_MUNSTKERR_Msk,  "MPU: зняття кадру виключення зі стека" },

    /* BusFault: шина відповіла помилкою або не відповіла зовсім. */
    { SCB_CFSR_IBUSERR_Msk,    "шина: вибірка інструкції за недійсною адресою" },
    { SCB_CFSR_PRECISERR_Msk,  "шина: точна помилка доступу — адреса в BFAR" },
    /*
     * Неточна помилка — прямий наслідок буфера запису: STR устиг «завершитися»
     * для конвеєра, ядро пішло далі, і лише потім шина сказала «ні». Ані BFAR,
     * ані PC у кадрі на винуватця вже не показують. Саме від цього рятує DSB
     * перед зміною маски.
     */
    { SCB_CFSR_IMPRECISERR_Msk, "шина: неточна помилка — запис завис у буфері" },
    { SCB_CFSR_STKERR_Msk,     "шина: складання кадру виключення на стек" },
    { SCB_CFSR_UNSTKERR_Msk,   "шина: зняття кадру виключення зі стека" },

    /* UsageFault: сама програма зробила те, чого архітектура не дозволяє. */
    { SCB_CFSR_DIVBYZERO_Msk,  "ділення на нуль (увімкнено CCR.DIV_0_TRP)" },
    { SCB_CFSR_UNALIGNED_Msk,  "невирівняний доступ до пам'яті" },
    { SCB_CFSR_NOCP_Msk,       "звернення до вимкненого співпроцесора (FPU?)" },
    { SCB_CFSR_INVPC_Msk,      "недійсний EXC_RETURN або PC при поверненні" },
    { SCB_CFSR_INVSTATE_Msk,   "перехід в ARM-стан: біт T у xPSR скинуто" },
    { SCB_CFSR_UNDEFINSTR_Msk, "невизначена інструкція" }
};

#endif /* !__ARM_ARCH_6M__ */

const char *fault_report_cause(const fault_record_t *rec)
{
    if (rec == NULL) {
        return "запису немає";
    }

#if !defined(__ARM_ARCH_6M__)
    if ((rec->hfsr & SCB_HFSR_VECTTBL_Msk) != 0U) {
        return "помилка читання таблиці векторів";
    }

    const size_t count = sizeof(k_cfsr_causes) / sizeof(k_cfsr_causes[0]);
    for (size_t i = 0U; i < count; ++i) {
        if ((rec->cfsr & k_cfsr_causes[i].mask) != 0U) {
            return k_cfsr_causes[i].text;
        }
    }

    if ((rec->hfsr & SCB_HFSR_DEBUGEVT_Msk) != 0U) {
        return "подія зневадження без підключеного зневадника";
    }
#endif

    return "HardFault без ознак у регістрах стану";
}

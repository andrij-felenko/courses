/* fault_handler.c — діагностичний обробник збою з витягуванням кадру стека.

   Обробник складається з двох половин, і це не примха стилю.

   Перша половина мусить бути асемблерною. Входячи у виняток, ядро вже уклало
   кадр R0–R3, R12, LR, PC, xPSR на той стек, який був активний, — і лише
   значення LR каже, на який саме: біт 2 коду EXC_RETURN розрізняє головний
   стек MSP і стек задачі PSP. Мовою C цього не написати: компілятор має право
   вставити власний пролог і зрушити SP раніше, ніж ми встигнемо його
   прочитати. Атрибут naked забороняє пролог, а обгортка лише кладе адресу
   кадру в R0, EXC_RETURN у R1 і стрибає далі — за AAPCS це вже два перші
   аргументи звичайної функції C.

   Друга половина — звичайна функція: читає регістри стану, складає звіт і
   спиняє ядро. */

#include <stdint.h>

#include "cortex_m.h"
#include "startup.h"

/* Кадр, який ядро уклало апаратно. Порядок полів заданий архітектурою. */
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;    /* адреса повернення з функції, що впала */
    uint32_t pc;    /* інструкція, на якій стався збій       */
    uint32_t psr;
} exception_frame_t;

typedef struct {
    exception_frame_t frame;
    uint32_t exception;     /* номер вектора з ICSR             */
    uint32_t cfsr;
    uint32_t hfsr;
    uint32_t mmfar;
    uint32_t bfar;
    uint32_t access_address; /* адреса доступу, якщо вона відома */
    uint8_t  address_valid;
    uint8_t  used_psp;       /* кадр лежав на стеку задачі       */
    uint8_t  escalated;      /* збій ескалював у HardFault       */
    const char *cause;       /* людська назва причини            */
} fault_record_t;

/* Останній зафіксований збій. Лежить у .bss, тож переживає лише поточний сеанс:
   після скидання стартовий код занулює цю пам'ять. Під GDB звіт читається
   однією командою `print g_last_fault`. */
fault_record_t g_last_fault;

void HardFault_Handler_C(uint32_t *stack_frame, uint32_t exc_return);

/* Асемблерна обгортка. Один і той самий текст потрібен чотирьом векторам,
   тому він оформлений макросом, а не скопійований чотири рази. */
#define FAULT_TRAMPOLINE(name)                                    \
    __attribute__((naked, used))                                  \
    void name(void)                                               \
    {                                                             \
        __asm volatile(                                           \
            ".syntax unified            \n"                       \
            "tst    lr, #4              \n" /* біт 2 EXC_RETURN */ \
            "ite    eq                  \n"                       \
            "mrseq  r0, msp             \n" /* 0 → кадр на MSP  */ \
            "mrsne  r0, psp             \n" /* 1 → кадр на PSP  */ \
            "mov    r1, lr              \n" /* сам EXC_RETURN   */ \
            "b      HardFault_Handler_C \n"                       \
        );                                                        \
    }

/* Сильні визначення перекривають слабкі псевдоніми зі стартового модуля. */
FAULT_TRAMPOLINE(HardFault_Handler)
FAULT_TRAMPOLINE(MemManage_Handler)
FAULT_TRAMPOLINE(BusFault_Handler)
FAULT_TRAMPOLINE(UsageFault_Handler)

/* Розбір CFSR згори вниз: перша ознака, що збіглася, і є причина. Порядок не
   випадковий — ознаки «липкі» й накопичуються, тож першим перевіряємо те, що
   точно вказує на винну інструкцію. */
static const char *decode_cause(uint32_t cfsr, uint32_t hfsr)
{
    if (cfsr & CFSR_DIVBYZERO)   { return "ділення цілого на нуль"; }
    if (cfsr & CFSR_UNALIGNED)   { return "невирівняний доступ"; }
    if (cfsr & CFSR_NOCP)        { return "інструкція FPU при вимкненому співпроцесорі"; }
    if (cfsr & CFSR_INVSTATE)    { return "стрибок за адресою без Thumb-біта"; }
    if (cfsr & CFSR_INVPC)       { return "невірне значення EXC_RETURN"; }
    if (cfsr & CFSR_UNDEFINSTR)  { return "невідома інструкція"; }
    if (cfsr & CFSR_PRECISERR)   { return "точна помилка шини (адреса в BFAR)"; }
    if (cfsr & CFSR_IMPRECISERR) { return "неточна помилка шини: винна відкладена запис-операція"; }
    if (cfsr & CFSR_IBUSERR)     { return "помилка шини при вибірці коду"; }
    if (cfsr & CFSR_DACCVIOL)    { return "заборонений доступ до даних (MPU)"; }
    if (cfsr & CFSR_IACCVIOL)    { return "вибірка коду із забороненої зони (MPU)"; }
    if (cfsr & CFSR_MSTKERR)     { return "збій при укладанні кадру винятку: переповнення стека"; }
    if (cfsr & CFSR_MUNSTKERR)   { return "збій при знятті кадру винятку"; }
    if (hfsr & SCB_HFSR_VECTTBL) { return "нечитний запис векторної таблиці"; }
    if (hfsr & SCB_HFSR_DEBUGEVT){ return "подія налагодження"; }
    return "причина не позначена в CFSR/HFSR";
}

/* Адреса доступу відома лише тоді, коли залізо саме сказало, що зафіксувало її:
   без MMARVALID чи BFARVALID у регістрі лежить значення від минулого разу. */
static uint8_t resolve_address(uint32_t cfsr, uint32_t mmfar, uint32_t bfar,
                               uint32_t *out)
{
    if (cfsr & CFSR_MMARVALID) { *out = mmfar; return 1U; }
    if (cfsr & CFSR_BFARVALID) { *out = bfar;  return 1U; }
    *out = 0U;
    return 0U;
}

/* Друга половина обробника. Викликається обгорткою й не повертається ніколи. */
__attribute__((used))
void HardFault_Handler_C(uint32_t *stack_frame, uint32_t exc_return)
{
    const uint32_t cfsr = CM_REG32(SCB_CFSR);
    const uint32_t hfsr = CM_REG32(SCB_HFSR);

    g_last_fault.frame     = *(const exception_frame_t *)stack_frame;
    g_last_fault.exception = cm_active_exception();
    g_last_fault.cfsr      = cfsr;
    g_last_fault.hfsr      = hfsr;
    g_last_fault.mmfar     = CM_REG32(SCB_MMFAR);
    g_last_fault.bfar      = CM_REG32(SCB_BFAR);
    g_last_fault.used_psp  = (exc_return & 4U) ? 1U : 0U;
    g_last_fault.escalated = (hfsr & SCB_HFSR_FORCED) ? 1U : 0U;
    g_last_fault.cause     = decode_cause(cfsr, hfsr);
    g_last_fault.address_valid =
        resolve_address(cfsr, g_last_fault.mmfar, g_last_fault.bfar,
                        &g_last_fault.access_address);

    /* Ознаки збою «липкі»: доки їх не скинути записом одиниць, наступний аналіз
       побачить причину минулого разу. Скидаємо ПІСЛЯ того, як звіт зібрано. */
    CM_REG32(SCB_CFSR) = cfsr;
    CM_REG32(SCB_HFSR) = hfsr;

    /* Зупинка під налагоджувачем саме тут: увесь контекст іще на місці, а
       g_last_fault.frame.pc віддається команді
       arm-none-eabi-addr2line -e firmware.elf <pc>. */
    cm_bkpt();

    for (;;) {
        cm_wfi();
    }
}

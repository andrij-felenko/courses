/* cortex_m.h — рівно та частина ядра Cortex-M, якої торкається стартовий код.
   Це не заміна CMSIS: тут лише регістри блоку SCB та кілька інструкцій, які
   мовою C не виражаються. Адреси й розкладка бітів — з ARMv7-M Architecture
   Reference Manual, розділ B3.2 (System Control Block). */

#ifndef CORTEX_M_H
#define CORTEX_M_H

#include <stdint.h>

/* Доступ до регістра ядра. volatile обов'язковий: значення міняє залізо, і
   компілятор не має права ані кешувати читання, ані викидати запис. */
#define CM_REG32(addr) (*(volatile uint32_t *)(addr))

/* ── Регістри System Control Block ─────────────────────────────────────────── */
#define SCB_ICSR   0xE000ED04U  /* стан і номер активного винятку            */
#define SCB_VTOR   0xE000ED08U  /* адреса векторної таблиці                  */
#define SCB_AIRCR  0xE000ED0CU  /* скидання системи, групування пріоритетів  */
#define SCB_CCR    0xE000ED14U  /* налаштування поведінки ядра               */
#define SCB_SHCSR  0xE000ED24U  /* дозвіл окремих обробників збоїв           */
#define SCB_CFSR   0xE000ED28U  /* причина збою: MemManage + BusFault + Usage */
#define SCB_HFSR   0xE000ED2CU  /* причина HardFault                          */
#define SCB_MMFAR  0xE000ED34U  /* адреса, що порушила захист MPU             */
#define SCB_BFAR   0xE000ED38U  /* адреса, на якій відмовила шина             */
#define SCB_CPACR  0xE000ED88U  /* доступ до співпроцесорів (FPU)             */

/* Повний доступ до CP10 і CP11 — обидва блоки FPU, по два біти на кожен. */
#define SCB_CPACR_CP10_CP11_FULL  (0xFU << 20)

/* Дозвіл окремих обробників у SHCSR. Доки біт не виставлено, ядро ескалює
   відповідний збій у HardFault замість виклику власного вектора. */
#define SCB_SHCSR_MEMFAULTENA  (1U << 16)
#define SCB_SHCSR_BUSFAULTENA  (1U << 17)
#define SCB_SHCSR_USGFAULTENA  (1U << 18)

/* CCR: пастка на ділення цілого на нуль і на невирівняний доступ. */
#define SCB_CCR_DIV_0_TRP   (1U << 4)
#define SCB_CCR_UNALIGN_TRP (1U << 3)

/* ICSR: молодші 9 бітів — номер винятку, що виконується просто зараз. */
#define SCB_ICSR_VECTACTIVE 0x1FFU

/* HFSR: FORCED означає, що збій прийшов не своїм вектором, а ескалював
   у HardFault; DEBUGEVT — зупинка через подію налагодження. */
#define SCB_HFSR_VECTTBL  (1U << 1)
#define SCB_HFSR_FORCED   (1U << 30)
#define SCB_HFSR_DEBUGEVT (1U << 31)

/* CFSR — три байти в одному слові. */
#define CFSR_MMARVALID (1U << 7)   /* MMFAR містить дійсну адресу       */
#define CFSR_MSTKERR   (1U << 4)   /* збій при укладанні кадру винятку  */
#define CFSR_MUNSTKERR (1U << 3)
#define CFSR_DACCVIOL  (1U << 1)   /* заборонений доступ до даних       */
#define CFSR_IACCVIOL  (1U << 0)   /* вибірка коду із забороненої зони  */

#define CFSR_BFARVALID (1U << 15)  /* BFAR містить дійсну адресу        */
#define CFSR_PRECISERR (1U << 9)   /* точна помилка шини: PC винен      */
#define CFSR_IMPRECISERR (1U << 10)/* неточна: винна відкладена запис-операція */
#define CFSR_IBUSERR   (1U << 8)

#define CFSR_DIVBYZERO (1U << 25)  /* ділення на нуль при DIV_0_TRP     */
#define CFSR_UNALIGNED (1U << 24)
#define CFSR_NOCP      (1U << 19)  /* інструкція FPU при вимкненому CP10 */
#define CFSR_INVPC     (1U << 18)
#define CFSR_INVSTATE  (1U << 17)  /* стрибок за адресою без Thumb-біта  */
#define CFSR_UNDEFINSTR (1U << 16)

/* ── Інструкції, яких у мові C немає ───────────────────────────────────────── */

/* Бар'єр даних: усі попередні звернення до пам'яті завершено. */
static inline void cm_dsb(void) { __asm volatile("dsb 0xF" ::: "memory"); }

/* Бар'єр інструкцій: конвеєр очищено, наступні команди декодуються заново. */
static inline void cm_isb(void) { __asm volatile("isb 0xF" ::: "memory"); }

/* Спинити ядро до наступного переривання — пастка, яка не гріє чіп. */
static inline void cm_wfi(void) { __asm volatile("wfi" ::: "memory"); }

/* Точка зупину: під налагоджувачем ядро спиняється саме тут, без
   налагоджувача інструкція дає HardFault (і це чесніше за тихий цикл). */
static inline void cm_bkpt(void) { __asm volatile("bkpt #0"); }

static inline uint32_t cm_get_msp(void)
{
    uint32_t result;
    __asm volatile("mrs %0, msp" : "=r"(result));
    return result;
}

/* Номер винятку, що виконується просто зараз: 0 — потоковий режим,
   3 — HardFault, 4 — MemManage, 5 — BusFault, 6 — UsageFault. */
static inline uint32_t cm_active_exception(void)
{
    return CM_REG32(SCB_ICSR) & SCB_ICSR_VECTACTIVE;
}

#endif /* CORTEX_M_H */

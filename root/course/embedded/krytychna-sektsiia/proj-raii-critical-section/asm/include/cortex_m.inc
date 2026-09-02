/*
 * Спільні означення асемблерних модулів драйвера критичних секцій.
 *
 * Файл підключається з кожного .S через препроцесор (gcc -x
 * assembler-with-cpp), тому тут вільно змішуються #define і директиви gas.
 */

#ifndef CORTEX_M_INC
#define CORTEX_M_INC

    .syntax unified
    .thumb

/* --- Блок налагодження ядра (System Control Space) ----------------------- */

#define CORE_DEBUG_DHCSR        0xE000EDF0  /* стан зневаджувача            */
#define CORE_DEBUG_DEMCR        0xE000EDFC  /* дозвіл трасування            */
#define DHCSR_C_DEBUGEN         (1 << 0)    /* зневаджувач під'єднано       */
#define DEMCR_TRCENA            (1 << 24)   /* живлення блоку трасування    */

/* --- Лічильник тактів DWT ------------------------------------------------ */

#define DWT_BASE                0xE0001000
#define DWT_CTRL_OFF            0x000
#define DWT_CYCCNT_OFF          0x004
#define DWT_LAR_OFF             0xFB0       /* CoreSight-замок блоку        */
#define DWT_CYCCNT_ADDR         (DWT_BASE + DWT_CYCCNT_OFF)
#define DWT_CTRL_CYCCNTENA      (1 << 0)
#define DWT_CTRL_NOCYCCNT       (1 << 25)   /* 1 — лічильника немає взагалі  */
#define DWT_LAR_KEY             0xC5ACCE55

/* --- Керування кешем Cortex-M7 ------------------------------------------- */

#define SCB_CTR                 0xE000ED7C  /* Cache Type Register          */
#define SCB_ICIALLU             0xE000EF50  /* інвалідація всього I-Cache   */
#define SCB_DCIMVAC             0xE000EF5C  /* інвалідація рядка за адресою */
#define SCB_DCCMVAC             0xE000EF68  /* виштовхування рядка          */
#define SCB_DCCIMVAC            0xE000EF70  /* виштовхування + інвалідація  */

/* --- Регістр пріоритетів NVIC -------------------------------------------- */

#define NVIC_IPR0               0xE000E400

/* --- Допоміжні макроси --------------------------------------------------- */

/*
 * Заголовок функції: власна секція (щоб лінкер викинув невживане з
 * -ffunction-sections), вирівнювання, .thumb_func — без нього лінкер не
 * поставить молодший біт адреси й перший же bl приведе в HardFault.
 */
    .macro CS_FUNC name
    .section .text.\name, "ax", %progbits
    .align  2
    .global \name
    .thumb_func
    .type   \name, %function
\name:
    .endm

    .macro CS_ENDF name
    .size \name, . - \name
    .endm

/*
 * Завантаження 32-бітної сталої парою movw/movt. Літерального пулу не
 * створює — а отже, не залежить від того, де gas вирішить його покласти
 * при розкладанні кожної функції в окрему секцію.
 * Доступно на ARMv7-M і новіших; на Cortex-M0 не вживаємо.
 */
    .macro CS_LDIMM32 reg, value
    movw \reg, #((\value) & 0xFFFF)
    movt \reg, #(((\value) >> 16) & 0xFFFF)
    .endm

#endif /* CORTEX_M_INC */

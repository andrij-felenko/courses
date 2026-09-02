/*
 * Тривалість критичної секції в тактах ядра — лічильник DWT->CYCCNT.
 *
 * Блок DWT є на Cortex-M3/M4/M7/M33; на M0/M0+ його немає, тому файл
 * згортається так само, як cs_basepri.S.
 */

#include "cortex_m.inc"

#if defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || \
    defined(__ARM_ARCH_8M_MAIN__)

/*
 * bool cs_dwt_enable(void)
 *
 * Повертає false, якщо лічильника в кристалі немає або він не побіг.
 * Мовчки міряти нулі гірше, ніж не міряти взагалі, тому перевіряємо ділом:
 * читаємо, робимо кілька тактів, читаємо ще раз.
 */
CS_FUNC cs_dwt_enable
    CS_LDIMM32 r1, CORE_DEBUG_DEMCR
    ldr     r0, [r1]
    orr     r0, r0, #DEMCR_TRCENA   @ подати живлення блоку трасування
    str     r0, [r1]
    dsb

    CS_LDIMM32 r1, DWT_BASE
    CS_LDIMM32 r2, DWT_LAR_KEY
    str     r2, [r1, #DWT_LAR_OFF]  @ на частині ядер блок замкнено CoreSight
    dsb

    ldr     r0, [r1, #DWT_CTRL_OFF]
    tst     r0, #DWT_CTRL_NOCYCCNT  @ 1 — лічильника тактів не реалізовано
    bne     .Ldwt_absent

    movs    r2, #0
    str     r2, [r1, #DWT_CYCCNT_OFF]
    orr     r0, r0, #DWT_CTRL_CYCCNTENA
    str     r0, [r1, #DWT_CTRL_OFF]

    ldr     r2, [r1, #DWT_CYCCNT_OFF]
    nop
    nop
    nop
    ldr     r3, [r1, #DWT_CYCCNT_OFF]
    cmp     r3, r2
    ite     ne
    movne   r0, #1
    moveq   r0, #0                  @ стоїть на місці — трасування без живлення
    bx      lr
.Ldwt_absent:
    movs    r0, #0
    bx      lr
CS_ENDF cs_dwt_enable

/* uint32_t cs_dwt_cycles(void) */
CS_FUNC cs_dwt_cycles
    CS_LDIMM32 r1, DWT_CYCCNT_ADDR
    ldr     r0, [r1]
    bx      lr
CS_ENDF cs_dwt_cycles

/*
 * bool cs_debugger_attached(void)
 *
 * __BKPT без під'єднаного зневаджувача — це HardFault, тож перед зупинкою на
 * зриві бюджету питаємо, чи є кому зупиняти.
 */
CS_FUNC cs_debugger_attached
    CS_LDIMM32 r1, CORE_DEBUG_DHCSR
    ldr     r0, [r1]
    and     r0, r0, #DHCSR_C_DEBUGEN
    cmp     r0, #0
    ite     eq
    moveq   r0, #0
    movne   r0, #1
    bx      lr
CS_ENDF cs_debugger_attached

/*
 * uint32_t cs_measure_enter_exit(void)
 *
 * Ціна пари «зберегти маску — замаскувати — відновити» в тактах.
 *
 * Хитрість вимірювання: читання самого CYCCNT теж коштує тактів, і на шині
 * налагодження воно коштує більше за арифметику. Тому спершу міряємо
 * порожній проміжок між двома читаннями (це наша похибка), потім той самий
 * проміжок із трьома інструкціями всередині, і віднімаємо.
 *
 * Увесь вимір іде під маскою: інакше в проміжок влізло б переривання й
 * додало б до результату свій час. CPSID усередині від цього не псується —
 * маскувати вже замасковане ядро можна скільки завгодно, а MSR PRIMASK
 * відновлює ту саму одиницю.
 */
CS_FUNC cs_measure_enter_exit
    push    {r4, r5, r6, lr}
    mrs     r6, PRIMASK
    cpsid   i
    CS_LDIMM32 r4, DWT_CYCCNT_ADDR

    ldr     r0, [r4]
    ldr     r1, [r4]
    subs    r5, r1, r0              @ r5 — похибка самого вимірювання

    ldr     r0, [r4]
    mrs     r2, PRIMASK             @ ┐
    cpsid   i                       @ ├ те, що робить вхід у секцію й вихід
    msr     PRIMASK, r2             @ ┘
    ldr     r1, [r4]
    subs    r0, r1, r0

    cmp     r0, r5
    ite     hi
    subhi   r0, r0, r5
    movls   r0, #0                  @ вимір потонув у похибці — чесніше 0

    msr     PRIMASK, r6
    pop     {r4, r5, r6, pc}
CS_ENDF cs_measure_enter_exit

/*
 * uint32_t cs_profile_call(void (*body)(void *), void *ctx)
 *
 * Виконати body(ctx) під маскою й повернути тривалість у тактах.
 *
 * Такти знімаємо ДО маскування й ПІСЛЯ відновлення — вартість самого входу
 * теж належить секції, бо саме її бачить обробник, що чекає на розмаскування.
 * Різниця беззнакових лишається правильною й тоді, коли 32-бітний лічильник
 * переповнився посеред виміру.
 */
CS_FUNC cs_profile_call
    push    {r4, r5, r6, r7, r8, lr}
    mov     r4, r0                  @ body
    mov     r5, r1                  @ ctx
    CS_LDIMM32 r6, DWT_CYCCNT_ADDR

    ldr     r8, [r6]
    mrs     r7, PRIMASK
    cpsid   i
    mov     r0, r5
    blx     r4                      @ тіло секції: винятків тут не буває
    msr     PRIMASK, r7
    ldr     r0, [r6]

    subs    r0, r0, r8
    pop     {r4, r5, r6, r7, r8, pc}
CS_ENDF cs_profile_call

#endif /* ARMv7-M / ARMv8-M Mainline */

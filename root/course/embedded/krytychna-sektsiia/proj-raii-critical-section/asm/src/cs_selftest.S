/*
 * Самоперевірка драйвера на живому кристалі.
 *
 * Хостові тести (c/test, cpp/test) перевіряють логіку вкладеності й
 * дострокових виходів на заглушці. Заглушка не скаже, чи справді MSR
 * PRIMASK діє на цьому кристалі, чи реалізовано BASEPRI, чи побіг лічильник
 * тактів — це видно лише на платі. Тому такий самий набір перевірок
 * повторюємо на старті прошивки, ще до запуску планувальника.
 *
 * Повертає 0 або набір бітів вад (значення дублює include/cs_asm.h).
 *
 * Кличеться з потокового режиму: усередині переривання на короткий час
 * вмикаються, наприкінці стан маски повертається таким, яким був.
 */

#include "cortex_m.inc"

#define ST_SAVED_STATE      (1 << 0)
#define ST_NOT_MASKED       (1 << 1)
#define ST_NOT_RESTORED     (1 << 2)
#define ST_NESTING          (1 << 3)
#define ST_PRIO_WEAKENED    (1 << 4)
#define ST_PRIO_SET         (1 << 5)
#define ST_CONTEXT          (1 << 6)
#define ST_DWT              (1 << 7)

/* uint32_t cs_selftest(void) */
CS_FUNC cs_selftest
    /* Шість регістрів — 24 байти: вирівнювання стека на 8 лишається цілим.
       r4 — накопичувач вад, r6 — вихідний PRIMASK, r7 — вихідний BASEPRI,
       r5 і r8 — робочі. */
    push    {r4, r5, r6, r7, r8, lr}
    movs    r4, #0
    mrs     r6, PRIMASK
    cpsie   i                       @ перевірка починається з відкритих переривань

    /* --- 1. Вхід повертає стан ДО себе й таки маскує ---------------------- */
    bl      cs_enter
    mov     r5, r0                  @ r5 — те, що треба віддати на виході
    cmp     r0, #0
    beq     .Lst_saved_ok
    orr     r4, r4, #ST_SAVED_STATE
.Lst_saved_ok:
    mrs     r0, PRIMASK
    cmp     r0, #1
    beq     .Lst_masked_ok
    orr     r4, r4, #ST_NOT_MASKED
.Lst_masked_ok:

    /* --- 2. Вкладеність: вихід із внутрішньої секції не розмасковує ------- */
    bl      cs_enter                @ r0 = 1 (маска вже стоїть)
    bl      cs_exit                 @ віддаємо назад те саме
    mrs     r0, PRIMASK
    cmp     r0, #1
    beq     .Lst_nesting_ok
    orr     r4, r4, #ST_NESTING
.Lst_nesting_ok:

    /* --- 3. Вихід із зовнішньої секції відновлює вихідний стан ------------ */
    mov     r0, r5
    bl      cs_exit
    mrs     r0, PRIMASK
    cmp     r0, #0
    beq     .Lst_restored_ok
    orr     r4, r4, #ST_NOT_RESTORED
.Lst_restored_ok:

#if defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || \
    defined(__ARM_ARCH_8M_MAIN__)
    /* --- 4. BASEPRI: поріг ставиться й ніколи не слабшає ------------------ */
    bl      cs_get_basepri
    mov     r7, r0                  @ вихідний поріг — повернемо наприкінці
    movs    r0, #0
    bl      cs_set_basepri          @ починаємо з чистого

    movs    r0, #0x50
    bl      cs_prio_enter
    bl      cs_get_basepri
    cmp     r0, #0x50
    beq     .Lst_prio_set_ok
    orr     r4, r4, #ST_PRIO_SET
.Lst_prio_set_ok:

    movs    r0, #0x70               @ слабший поріг — має бути відкинутий
    bl      cs_set_basepri_max
    bl      cs_get_basepri
    cmp     r0, #0x50
    beq     .Lst_prio_keep_ok
    orr     r4, r4, #ST_PRIO_WEAKENED
.Lst_prio_keep_ok:

    movs    r0, #0x30               @ суворіший — має пройти
    bl      cs_set_basepri_max
    bl      cs_get_basepri
    cmp     r0, #0x30
    beq     .Lst_prio_tight_ok
    orr     r4, r4, #ST_PRIO_SET
.Lst_prio_tight_ok:

    mov     r0, r7
    bl      cs_prio_exit            @ повернути поріг, який був до перевірки
#endif

    /* --- 5. Контекст: у потоковому режимі IPSR мусить бути нульовий ------- */
    bl      cs_in_interrupt_context
    cmp     r0, #0
    beq     .Lst_context_ok
    orr     r4, r4, #ST_CONTEXT
.Lst_context_ok:

#if defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || \
    defined(__ARM_ARCH_8M_MAIN__)
    /* --- 6. Лічильник тактів справді біжить ------------------------------- */
    bl      cs_dwt_enable
    cmp     r0, #0
    beq     .Lst_dwt_bad
    bl      cs_dwt_cycles
    mov     r8, r0
    nop
    nop
    nop
    nop
    bl      cs_dwt_cycles
    cmp     r0, r8
    bne     .Lst_dwt_ok
.Lst_dwt_bad:
    orr     r4, r4, #ST_DWT
.Lst_dwt_ok:
#endif

    mov     r0, r6                  @ маску — такою, якою застали
    bl      cs_set_primask
    mov     r0, r4
    pop     {r4, r5, r6, r7, r8, pc}
CS_ENDF cs_selftest

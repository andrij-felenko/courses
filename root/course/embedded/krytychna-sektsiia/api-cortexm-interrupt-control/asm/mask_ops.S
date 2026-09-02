/*
 * mask_ops.S — примітиви маскування переривань Cortex-M чистим Thumb-2.
 *
 * Це не обгортка над CMSIS, а рівно те, у що CMSIS розгортається. Кожна
 * функція дотримується AAPCS (єдиний аргумент у r0, результат у r0), тож
 * викликається з C як звичайна: див. оголошення в c/cortexm_mask.h.
 *
 * Розширення .S (велике) — файл проходить через препроцесор, тому працюють
 * #if: на ARMv6-M (Cortex-M0/M0+) регістрів BASEPRI та FAULTMASK просто немає,
 * і асемблер відмовиться складати MSR BASEPRI для такої цілі.
 */

    .syntax unified
    .thumb

/* ---- PRIMASK: глобальна маска всіх настроюваних переривань ------------- */

    .section .text.mask_primask_save_disable,"ax",%progbits
    .global  mask_primask_save_disable
    .type    mask_primask_save_disable,%function
    .thumb_func
    .align   2
mask_primask_save_disable:
    mrs     r0, PRIMASK         /* спершу зберігаємо старий стан...           */
    cpsid   i                   /* ...і аж потім маскуємо: PRIMASK = 1        */
    bx      lr                  /* r0 = стан ДО входу, його й повертаємо      */
    .size   mask_primask_save_disable, . - mask_primask_save_disable

    .section .text.mask_primask_restore,"ax",%progbits
    .global  mask_primask_restore
    .type    mask_primask_restore,%function
    .thumb_func
    .align   2
mask_primask_restore:
    dsb                         /* записи секції мають фізично дійти до пам'яті */
    msr     PRIMASK, r0         /* саме відновлення, а не безумовне CPSIE i     */
    isb                         /* конвеєр перечитує стан: відкладені IRQ — вже  */
    bx      lr
    .size   mask_primask_restore, . - mask_primask_restore

/* ---- IPSR: номер активного виключення (є на всіх профілях) ------------- */

    .section .text.mask_active_exception,"ax",%progbits
    .global  mask_active_exception
    .type    mask_active_exception,%function
    .thumb_func
    .align   2
mask_active_exception:
    mrs     r0, IPSR            /* 0 — Thread Mode; >=16 — зовнішній IRQ (n-16) */
    bx      lr
    .size   mask_active_exception, . - mask_active_exception

#if !defined(__ARM_ARCH_6M__)

/* ---- BASEPRI: поріг пріоритету (ARMv7-M і ARMv8-M Mainline) ------------ */

    .section .text.mask_basepri_raise,"ax",%progbits
    .global  mask_basepri_raise
    .type    mask_basepri_raise,%function
    .thumb_func
    .align   2
mask_basepri_raise:
    mrs     r1, BASEPRI         /* старий поріг — у r1                        */
    msr     BASEPRI_MAX, r0     /* умовний запис: поріг лише посилюється      */
    mov     r0, r1              /* повертаємо старий поріг для симетричного   */
    bx      lr                  /* відновлення                                */
    .size   mask_basepri_raise, . - mask_basepri_raise

    .section .text.mask_basepri_restore,"ax",%progbits
    .global  mask_basepri_restore
    .type    mask_basepri_restore,%function
    .thumb_func
    .align   2
mask_basepri_restore:
    dsb
    msr     BASEPRI, r0         /* тут потрібен безумовний запис: MAX ослабити */
    isb                         /* поріг не вміє й секцію не закрив би         */
    bx      lr
    .size   mask_basepri_restore, . - mask_basepri_restore

/* ---- FAULTMASK: блокує навіть HardFault (пріоритет виконання -1) ------- */
/* ⚠ Помилка шини всередині такої секції = Lockup State, лише апаратний    */
/*   Reset або Watchdog. Апаратура сама скидає FAULTMASK при поверненні    */
/*   з будь-якого обробника, окрім NMI.                                    */

    .section .text.mask_faultmask_save_disable,"ax",%progbits
    .global  mask_faultmask_save_disable
    .type    mask_faultmask_save_disable,%function
    .thumb_func
    .align   2
mask_faultmask_save_disable:
    mrs     r0, FAULTMASK
    cpsid   f
    bx      lr
    .size   mask_faultmask_save_disable, . - mask_faultmask_save_disable

    .section .text.mask_faultmask_restore,"ax",%progbits
    .global  mask_faultmask_restore
    .type    mask_faultmask_restore,%function
    .thumb_func
    .align   2
mask_faultmask_restore:
    dsb
    msr     FAULTMASK, r0
    isb
    bx      lr
    .size   mask_faultmask_restore, . - mask_faultmask_restore

#endif /* !__ARM_ARCH_6M__ */

/*
 * Телеметричний пакет навігації, написаний руками.
 *
 * Це двійник того, що компілятор виготовив із C++ методу update (лістинг —
 * у asm/navigation_update.s). Тримати його поруч варто з двох причин: він
 * показує, скільки коду насправді стоїть за RAII-вартовим, і він же
 * показує ціну ручного письма — у nav_asm_snapshot відновлення маски
 * доводиться зводити на спільний вихід руками, і саме цей крок забувають.
 *
 * Розкладку структури функції знають числами; стереже її набір
 * _Static_assert в include/cs_asm.h:
 *   fix.latitude 0, longitude 4, altitude_mm 8, timestamp_us 16 (розмір 24)
 *   has_fix 24, updates 28
 */

#include "cortex_m.inc"

/*
 * void nav_asm_update(nav_state_t *self, const nav_fix_t *fix)
 *
 * Контекст: обробник переривання GNSS, приблизно 100 Гц.
 * Мітку часу переносимо однією парою ldrd/strd: два окремі 32-бітні записи
 * дали б читачеві мітку, зшиту з двох різних фіксів.
 */
CS_FUNC nav_asm_update
    push    {r4, r5}                @ 8 байтів — вирівнювання стека ціле
    mrs     r12, PRIMASK            @ r12 — робочий за AAPCS, зберігати не треба
    cpsid   i

    ldrd    r4, r5, [r1, #16]       @ timestamp_us джерела
    ldr     r2, [r1, #0]
    ldr     r3, [r1, #4]
    str     r2, [r0, #0]            @ latitude
    str     r3, [r0, #4]            @ longitude
    ldr     r2, [r1, #8]
    str     r2, [r0, #8]            @ altitude_mm
    strd    r4, r5, [r0, #16]       @ мітка — одним 64-бітним записом
    movs    r3, #1
    strb    r3, [r0, #24]           @ has_fix = true
    ldr     r2, [r0, #28]           @ ++updates: читання-зміна-запис
    adds    r2, r2, #1              @   неподільне лише під маскою
    str     r2, [r0, #28]

    msr     PRIMASK, r12            @ відновити, а не ввімкнути
    pop     {r4, r5}
    bx      lr
CS_ENDF nav_asm_update

/*
 * bool nav_asm_snapshot(const nav_state_t *self, nav_fix_t *out)
 *
 * Контекст: фонова задача телеметрії.
 *
 * Тут і живе та сама вада, від якої рятує вартовий: гілка «фікса ще немає»
 * — це достроковий вихід, і на ньому теж треба відновити PRIMASK. У C++ це
 * робить деструктор і забути неможливо; у C — атрибут cleanup; тут —
 * єдиний спільний вихід .Lsnap_out, до якого мусить прийти кожна гілка.
 */
CS_FUNC nav_asm_snapshot
    push    {r4, r5}
    mrs     r12, PRIMASK
    cpsid   i

    ldrb    r2, [r0, #24]           @ has_fix
    cbz     r2, .Lsnap_no_fix

    ldr     r2, [r0, #0]
    ldr     r3, [r0, #4]
    str     r2, [r1, #0]
    str     r3, [r1, #4]
    ldr     r2, [r0, #8]
    str     r2, [r1, #8]
    ldrd    r4, r5, [r0, #16]
    strd    r4, r5, [r1, #16]
    movs    r0, #1
    b       .Lsnap_out
.Lsnap_no_fix:
    movs    r0, #0
.Lsnap_out:
    msr     PRIMASK, r12
    pop     {r4, r5}
    bx      lr
CS_ENDF nav_asm_snapshot

/*
 * uint32_t nav_asm_updates(const nav_state_t *self)
 *
 * Секції немає навмисно: вирівняне 32-бітне читання на Cortex-M неподільне
 * саме собою, а маскувати переривання заради одного LDR — це подовжувати
 * латентність без жодної користі.
 */
CS_FUNC nav_asm_updates
    ldr     r0, [r0, #28]
    bx      lr
CS_ENDF nav_asm_updates

/* void nav_asm_reset(nav_state_t *self) */
CS_FUNC nav_asm_reset
    mrs     r12, PRIMASK
    cpsid   i
    movs    r1, #0
    strb    r1, [r0, #24]
    str     r1, [r0, #28]
    msr     PRIMASK, r12
    bx      lr
CS_ENDF nav_asm_reset

/*
 * Діагностика контексту виконання.
 *
 * Питання «мене звуть із задачі чи з обробника переривання?» вирішує вибір
 * примітиву: taskENTER_CRITICAL() з ISR валить систему через configASSERT().
 * Відповідь дають два спеціальні регістри, і обидва читаються однією
 * інструкцією MRS — на будь-якому ядрі Cortex-M.
 */

#include "cortex_m.inc"

/*
 * uint32_t cs_get_ipsr(void)
 *
 * Номер винятку, який ядро обробляє просто зараз. 0 — потоковий режим.
 * Значення 1 не буває: одиницю має сам скидач, а він уже не виконується.
 * 15 — SysTick, від 16 — зовнішні переривання (IRQn + 16).
 */
CS_FUNC cs_get_ipsr
    mrs     r0, IPSR
    bx      lr
CS_ENDF cs_get_ipsr

/* bool cs_in_interrupt_context(void) */
CS_FUNC cs_in_interrupt_context
    mrs     r0, IPSR
    cmp     r0, #0
    ite     eq
    moveq   r0, #0
    movne   r0, #1                  @ _Bool віддаємо як рівно 0 або 1
    bx      lr
CS_ENDF cs_in_interrupt_context

/*
 * uint32_t cs_get_control(void)
 *
 * Біт 0 (nPRIV) — потоковий режим непривілейований; біт 1 (SPSEL) — потік
 * працює на власному стеку PSP; біт 2 (FPCA) — кадр містить регістри FPU.
 */
CS_FUNC cs_get_control
    mrs     r0, CONTROL
    bx      lr
CS_ENDF cs_get_control

/*
 * bool cs_is_privileged(void)
 *
 * Важить тому, що CPSID/MSR PRIMASK з непривілейованого коду не спрацьовують
 * і не спричиняють винятку: інструкція просто нічого не робить. Критична
 * секція в задачі, запущеній непривілейовано, мовчки не захищає нічого.
 */
CS_FUNC cs_is_privileged
    mrs     r0, IPSR
    cbnz    r0, .Lpriv_handler      @ у режимі обробника — завжди привілей
    mrs     r0, CONTROL
    and     r0, r0, #1              @ nPRIV
    eor     r0, r0, #1
    bx      lr
.Lpriv_handler:
    movs    r0, #1
    bx      lr
CS_ENDF cs_is_privileged

/*
 * Глобальне маскування переривань через PRIMASK.
 *
 * Працює на кожному ядрі Cortex-M, включно з M0/M0+: тут немає ні movw/movt,
 * ні звертань до пам'яті — самі лише MRS/MSR/CPS.
 *
 * Виклик коштує дорожче за інлайнову версію рівно на bl і bx lr, зате ціна
 * тіла тут стала й видима очима: три інструкції, по одному такту кожна.
 */

#include "cortex_m.inc"

/* uint32_t cs_get_primask(void) */
CS_FUNC cs_get_primask
    mrs     r0, PRIMASK
    bx      lr
CS_ENDF cs_get_primask

/* void cs_set_primask(uint32_t value) */
CS_FUNC cs_set_primask
    msr     PRIMASK, r0
    bx      lr
CS_ENDF cs_set_primask

/* void cs_disable_irq(void) — беззастережне маскування, без збереження. */
CS_FUNC cs_disable_irq
    cpsid   i
    bx      lr
CS_ENDF cs_disable_irq

/*
 * void cs_enable_irq(void)
 *
 * Пряме вмикання, яке в тексті названо джерелом обох типових вад: із
 * середини вкладеної секції воно відкриває переривання завчасно. Функція
 * тут потрібна для старту системи й для виходу з режиму відмови, а не для
 * закриття критичних секцій — для цього є cs_exit.
 */
CS_FUNC cs_enable_irq
    cpsie   i
    bx      lr
CS_ENDF cs_enable_irq

/*
 * uint32_t cs_enter(void)
 *
 * Повертає стан PRIMASK до входу. Викликова угода AAPCS вимагає результату
 * в r0, тож повернення структури з єдиним 32-бітним полем (critical_section_t
 * із заголовка C) двійково збігається з цією функцією.
 */
CS_FUNC cs_enter
    mrs     r0, PRIMASK
    cpsid   i
    bx      lr
CS_ENDF cs_enter

/*
 * void cs_exit(uint32_t saved)
 *
 * Відновлення, а не вмикання: вихід із внутрішньої секції не відкриє
 * переривань, поки триває зовнішня.
 */
CS_FUNC cs_exit
    msr     PRIMASK, r0
    bx      lr
CS_ENDF cs_exit

/*
 * uint32_t cs_enter_sync(void)
 *
 * Те саме плюс бар'єри. CPSID діє на наступні інструкції одразу, але буфер
 * запису ядра може ще тримати незавершені звертання до периферії, а конвеєр
 * — уже вибрані інструкції. Коли одразу за межею секції йде запис у регістр
 * пристрою, зміна VTOR чи перемикання стека, платимо кілька тактів за DSB та
 * ISB і дістаємо певність. У звичайному оновленні полів структури це зайве.
 */
CS_FUNC cs_enter_sync
    mrs     r0, PRIMASK
    cpsid   i
    dsb
    isb
    bx      lr
CS_ENDF cs_enter_sync

/*
 * void cs_exit_sync(uint32_t saved)
 *
 * DSB перед розмаскуванням: усі записи секції мусять дійти до пам'яті
 * раніше, ніж їх побачить перший же обробник переривання.
 */
CS_FUNC cs_exit_sync
    dsb
    msr     PRIMASK, r0
    isb
    bx      lr
CS_ENDF cs_exit_sync

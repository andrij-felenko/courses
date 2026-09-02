/*
 * Кеш даних та інструкцій Cortex-M7.
 *
 * Вимкнених переривань замало, коли буфер після секції читає контролер DMA:
 * свіжі байти можуть лежати в L1 D-Cache, а DMA ходить по шині AXI просто в
 * ОЗП. Ці функції — те, у що розгортається SCB_CleanDCache_by_Addr із CMSIS.
 *
 * Модуль збирається, лише коли визначено CS_HAS_DCACHE (Makefile робить це
 * для CPU=cortex-m7): на ядрах без кешу регістрів за цими адресами немає.
 */

#include "cortex_m.inc"

#if defined(CS_HAS_DCACHE) && (CS_HAS_DCACHE)

/*
 * uint32_t cs_dcache_line_size(void)
 *
 * Cache Type Register, поле DminLine [19:16] — розмір найменшого рядка кешу
 * даних у словах як степінь двійки. На Cortex-M7 це 3, тобто 32 байти.
 * Читаємо, а не вписуємо сталу: те саме тіло має працювати й на M55.
 */
CS_FUNC cs_dcache_line_size
    CS_LDIMM32 r1, SCB_CTR
    ldr     r0, [r1]
    ubfx    r0, r0, #16, #4
    movs    r1, #4
    lsl     r0, r1, r0              @ байтів = 4 << DminLine
    bx      lr
CS_ENDF cs_dcache_line_size

/*
 * Тіло всіх трьох операцій над діапазоном однакове й різниться лише
 * регістром, у який пишуть адресу рядка. Тому — макрос.
 *
 * Початок вирівнюємо вниз на межу рядка й ідемо, поки не перетнули кінець:
 * рядок, у який потрапив хоч один байт діапазону, має бути оброблений.
 */
    .macro CS_DCACHE_RANGE fname, mvareg, needs_clean
    CS_FUNC \fname
    push    {r4, r5, r6, lr}
    cbz     r1, .Lrange_done\@      @ порожній діапазон
    adds    r5, r0, r1              @ кінець, виключно
    mov     r4, r0
    bl      cs_dcache_line_size
    subs    r6, r0, #1              @ маска молодших бітів адреси
    bic     r4, r4, r6              @ початок — на межу рядка
    CS_LDIMM32 r3, \mvareg
    dsb                             @ записи ядра мають дійти до кешу
.Lrange_loop\@:
    str     r4, [r3]                @ адреса рядка в регістр операції
    add     r4, r4, r0
    cmp     r4, r5
    blo     .Lrange_loop\@          @ порівняння адрес — беззнакове
    dsb                             @ операція завершилась
    isb
.Lrange_done\@:
    pop     {r4, r5, r6, pc}
    CS_ENDF \fname
    .endm

/*
 * void cs_dcache_clean_range(const void *addr, uint32_t size)
 *
 * Виштовхнути змінені рядки в ОЗП. Кличеться ПЕРЕД тим, як DMA почне читати
 * буфер, і — за текстом — ще до розмаскування переривань: інакше між
 * виходом із секції та чисткою кешу встигне влізти обробник, який запустить
 * передавання.
 */
    CS_DCACHE_RANGE cs_dcache_clean_range, SCB_DCCMVAC, 1

/*
 * void cs_dcache_invalidate_range(const void *addr, uint32_t size)
 *
 * Викинути рядки, не зберігаючи: кличеться ПІСЛЯ того, як DMA записав у
 * буфер, щоб наступне читання пішло в ОЗП, а не взяло старе з кешу.
 *
 * Пастка, через яку це найчастіше ламається: якщо буфер не вирівняний на
 * рядок, у крайні рядки потрапляють сусідні змінні — і їхні свіжі значення
 * буде втрачено разом із рядком. Тому буфери під DMA оголошують з
 * __attribute__((aligned(32))) і розміром, кратним рядку.
 */
    CS_DCACHE_RANGE cs_dcache_invalidate_range, SCB_DCIMVAC, 0

/*
 * void cs_dcache_clean_invalidate_range(const void *addr, uint32_t size)
 *
 * Виштовхнути й одразу викинути. Потрібно для буфера, який працює в обидва
 * боки: ми дописали заголовок кадру, а тіло в цей самий буфер покладе DMA.
 */
    CS_DCACHE_RANGE cs_dcache_clean_invalidate_range, SCB_DCCIMVAC, 1

/*
 * void cs_icache_invalidate_all(void)
 *
 * Потрібно після того, як у пам'ять покладено новий виконуваний код:
 * завантажувач прийняв прошивку, ділянку перепрограмовано, поставлено
 * перехідник. Кеш інструкцій інакше виконає те, що лежало там раніше.
 */
CS_FUNC cs_icache_invalidate_all
    CS_LDIMM32 r1, SCB_ICIALLU
    movs    r0, #0
    dsb
    str     r0, [r1]
    dsb
    isb
    bx      lr
CS_ENDF cs_icache_invalidate_all

#endif /* CS_HAS_DCACHE */

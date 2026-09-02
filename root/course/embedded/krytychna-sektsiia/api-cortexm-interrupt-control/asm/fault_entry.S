/*
 * fault_entry.S — пролог обробників помилок ядра.
 *
 * Обробник помилки не буває звичайною C-функцією. Йому потрібен покажчик на
 * кадр, який апаратура поклала на стек перед входом, а на який саме стек —
 * MSP чи PSP — знає лише EXC_RETURN, що лежить у LR у момент входу. Мовою C
 * цього не з'ясувати: значення LR зникне на першому ж пролозі компілятора,
 * і покажчик на кадр буде вгадуванням.
 *
 * Пролог складає AAPCS-виклик
 *     fault_entry_to_c(frame, exc_return, kind)
 * і переходить у нього хвостовим `b`, не чіпаючи ані кадру, ані стека: усе,
 * що апаратура зберегла, лишається доступним для посмертного розбору.
 */

    .syntax unified
    .thumb

/*
 * kind: 0 — HardFault, 1 — MemManage, 2 — BusFault, 3 — UsageFault.
 *
 * Розгалуження зроблено на `b`, а не на IT-блоці з mrseq/mrsne: ARMv6-M
 * умовного виконання не має взагалі, і той самий файл має складатися й під
 * Cortex-M0. Два зайві такти в обробнику аварії ніхто не помітить.
 */
    .macro FAULT_ENTRY name, kind
    .section .text.\name,"ax",%progbits
    .global  \name
    .type    \name,%function
    .thumb_func
    .align   2
\name:
    mov     r1, lr              /* EXC_RETURN — другий аргумент, як він є    */
    movs    r0, #4              /* біт 2 EXC_RETURN: 1 — кадр лежить на PSP  */
    tst     r1, r0
    beq     1f
    mrs     r0, PSP             /* помилка застала код потоку зі своїм стеком */
    b       2f                  /* (задача RTOS)                              */
1:
    mrs     r0, MSP             /* головний стек: фон без RTOS або вкладене   */
2:
    movs    r2, #\kind
    b       fault_entry_to_c    /* хвостовий перехід: кадр на стеку цілий     */
    .size   \name, . - \name
    .endm

    FAULT_ENTRY HardFault_Handler, 0

#if !defined(__ARM_ARCH_6M__)

/*
 * На ARMv6-M настроюваних обробників помилок не існує: усе, що на M3/M4/M7
 * стало б MemManage, BusFault чи UsageFault, там одразу приходить HardFault-ом.
 * Тобто ескалація на M0 не подія, а єдиний можливий режим.
 */

    FAULT_ENTRY MemManage_Handler,  1
    FAULT_ENTRY BusFault_Handler,   2
    FAULT_ENTRY UsageFault_Handler, 3

#endif /* !__ARM_ARCH_6M__ */

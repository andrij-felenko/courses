void vPortPendSVHandler(void) {
    /* 1. Збереження R4-R11 поточної задачі на PSP */
    __asm volatile("mrs r0, psp\n stmdb r0!, {r4-r11}\n");

    /* 2. Оновлення вказівника стека в TCB */
    /* 3. Вибір наступної готової задачі pxCurrentTCB */

    /* 4. Оновлення регіонів MPU для нової задачі */
    mpu_switch_task_context(&(pxCurrentTCB->isolation_desc));

    /* 5. Відновлення R4-R11 нової задачі з PSP */
    __asm volatile("ldmia r0!, {r4-r11}\n msr psp, r0\n bx lr\n");
}

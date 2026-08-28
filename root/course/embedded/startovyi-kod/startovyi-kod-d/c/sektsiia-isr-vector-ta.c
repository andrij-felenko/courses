/* Оголошення векторної таблиці мовою C */
__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))(&_estack), /* 0x00: Initial SP */
    Reset_Handler,              /* 0x04: Reset Handler */
    NMI_Handler,                /* 0x08: NMI Handler */
    HardFault_Handler,          /* 0x0C: HardFault Handler */
    MemManage_Handler,          /* 0x10: MPU Fault Handler */
    BusFault_Handler,           /* 0x14: Bus Fault Handler */
    UsageFault_Handler,         /* 0x18: Usage Fault Handler */
    0, 0, 0, 0,                 /* 0x1C..0x28: Reserved */
    SVC_Handler,                /* 0x2C: SVCall Handler */
    0,                          /* 0x30: Debug Monitor */
    0,                          /* 0x34: Reserved */
    PendSV_Handler,             /* 0x38: PendSV Handler */
    SysTick_Handler,            /* 0x3C: SysTick Handler */
    /* Далі розміщуються вектори периферії: WWDG_IRQHandler, PVD_IRQHandler... */
};

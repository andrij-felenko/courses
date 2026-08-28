/* Захисна пастка після виходу з main мовою C */
void Reset_Handler(void) {
    /* 1. Ініціалізація даних та рантайму */
    init_memory_sections();
    enable_fpu_coprocessor();
    SystemInit();
    invoke_global_constructors();

    /* 2. Запуск основної програми */
    main();

    /* 3. Якщо main() повернув значення — переходимо в режим очікування */
    while (1) {
        /* Команда Wait For Interrupt: вимикає тактування ядра до переривання */
        __asm volatile("wfi");
    }
}

/* Захисна пастка після виходу з main мовою C++ */
extern "C" void Reset_Handler() {
    /* 1. Ініціалізація даних та рантайму */
    mcu::startup::init_memory_sections();
    mcu::hardware::enable_fpu();
    SystemInit();
    mcu::runtime::call_global_constructors();

    /* 2. Запуск основної програми */
    static_cast<void>(main());

    /* 3. Термінальний енергозберігаючий цикл */
    while (true) {
        asm volatile("wfi");
    }
}

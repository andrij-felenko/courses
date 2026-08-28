#include <stdint.h>

// Базова адреса System Memory для конкретного мікроконтролера (наприклад, STM32F4)
#define SYSTEM_ROM_BASE  0x1FFF0000U

// Програмний перехід у фабричний завантажувач із коду користувача
void jump_to_bootloader(void)
{
    // 1. Повністю вимикаємо переривання, щоб жоден обробник не перервав деініціалізацію
    __asm volatile ("cpsid i" : : : "memory");

    // 2. Зупиняємо SysTick таймер і скидаємо його значення
    SysTick->CTRL = 0;
    SysTick->LOAD = 0;
    SysTick->VAL  = 0;

    // 3. Вимикаємо всі лінії переривань у контролері NVIC
    for (uint32_t i = 0; i < 8; ++i) {
        NVIC->ICER[i] = 0xFFFFFFFFU; // Вимкнути переривання
        NVIC->ICPR[i] = 0xFFFFFFFFU; // Очистити очікуючі запити
    }

    // 4. Бар'єр пам'яті для гарантування завершення всіх шинних транзакцій
    __asm volatile ("dsb 0xF" : : : "memory");
    __asm volatile ("isb 0xF" : : : "memory");

    // 5. Встановлюємо таблицю векторів переривань на початок System ROM
    SCB->VTOR = SYSTEM_ROM_BASE;

    // 6. Отримуємо значення початкового покажчика стека (MSP) та точку входу (Reset Vector)
    uint32_t boot_msp = *(volatile uint32_t *)(SYSTEM_ROM_BASE);
    uint32_t boot_reset_handler = *(volatile uint32_t *)(SYSTEM_ROM_BASE + 4);

    // 7. Встановлюємо вказівник стека ядра на стек завантажувача
    __set_MSP(boot_msp);

    // 8. Перетворюємо адресу Reset Handler на покажчик на функцію та стрибаємо
    void (*bootloader_entry)(void) = (void (*)(void))boot_reset_handler;
    bootloader_entry();

    // Сюди процесор ніколи не повернеться
    while (1) {}
}

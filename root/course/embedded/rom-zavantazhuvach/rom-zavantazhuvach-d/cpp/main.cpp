#include <cstdint>
#include <span>
#include <concepts>

// Базова адреса System Memory (задається згідно з документацією кристала)
inline constexpr std::uintptr_t SystemRomBase = 0x1FFF0000U;

class SystemBootloaderLauncher {
public:
    // Безпечний програмний стрибок у ROM-завантажувач
    [[noreturn]] static void launch() noexcept {
        // 1. Блокуємо глобальні переривання
        __asm volatile ("cpsid i" : : : "memory");

        // 2. Деактивуємо системний таймер SysTick
        SysTick->CTRL = 0;
        SysTick->LOAD = 0;
        SysTick->VAL  = 0;

        // 3. Очищаємо конфігурацію NVIC
        for (auto& icer : NVIC->ICER) {
            icer = 0xFFFFFFFFU;
        }
        for (auto& icpr : NVIC->ICPR) {
            icpr = 0xFFFFFFFFU;
        }

        // 4. Бар'єри синхронізації інструкцій та шини даних
        __asm volatile ("dsb 0xF" : : : "memory");
        __asm volatile ("isb 0xF" : : : "memory");

        // 5. Перепризначаємо зміщення таблиці векторів
        SCB->VTOR = SystemRomBase;

        // 6. Вичитуємо вектори завантажувача
        const auto* rom_vectors = reinterpret_cast<const volatile std::uint32_t*>(SystemRomBase);
        const std::uint32_t initial_msp = rom_vectors[0];
        const std::uint32_t reset_vector = rom_vectors[1];

        // 7. Налаштовуємо вказівник стека
        __set_MSP(initial_msp);

        // 8. Передаємо керування за адресою вектора скидання
        using EntryFn = void (*)() noexcept;
        const auto boot_entry = reinterpret_cast<EntryFn>(reset_vector);
        boot_entry();

        while (true) {
            __builtin_unreachable();
        }
    }
};

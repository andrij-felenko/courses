// weak_forms.c — три форми використання слабких символів у C99
#include <stdio.h>
#include <stdint.h>

// 1. Слабке визначення (Weak Definition)
// Якщо застосунок не визначить власну функцію log_event,
// лінкер збереже це базове тіло.
__attribute__((weak)) void log_event(const char* msg)
{
    printf("[DEFAULT LOG]: %s\n", msg);
}

// 2. Спільна функція-заглушка для слабких псевдонімів
void Default_Handler(void)
{
    // Нескінченна пастка або безпечна заглушка
    while (1) {
        // Очікування переривання або скидання сторожового таймера
    }
}

// Слабкий псевдонім (Weak Alias)
// Оголошує символ SysTick_Handler слабким і спрямовує його
// на адресу функції Default_Handler, якщо користувач не надасть сильного тіла.
void SysTick_Handler(void) __attribute__((weak, alias("Default_Handler")));
void USART1_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));

// 3. Слабке посилання (Weak Reference)
// Повідомляє лінкеру, що функція hardware_crypto_init може існувати,
// а може бути відсутньою у двійковому образі.
extern __attribute__((weak)) void hardware_crypto_init(void);

void system_startup(void)
{
    log_event("Ініціалізація підсистем...");

    // Обов'язкова перевірка адреси слабкого посилання перед викликом!
    if (hardware_crypto_init != NULL) {
        hardware_crypto_init();
    } else {
        printf("Апаратний криптомодуль не знайдено, використовуємо софтверний fallback.\n");
    }
}

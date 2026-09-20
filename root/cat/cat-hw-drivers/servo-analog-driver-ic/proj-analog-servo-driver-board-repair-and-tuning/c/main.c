#include <stdio.h>
#include <stdbool.h>
#include "servo_tester.h"

// Симульований екземпляр апаратного таймера MCU
static servo_timer_regs_t TIM2_Hardware;

// Затримка в мілісекундах (симуляція для випробувального стенда)
static void delay_ms(uint32_t ms) {
    // В реальній системі — HAL_Delay(ms) або системний таймер SysTick
    (void)ms;
}

int main(void) {
    printf("=== Випробування та калібрування серводрайверів AA5188 / KC0032 (C) ===\n");

    servo_tester_t tester;
    uint32_t system_clock = 16000000U; // 16 МГц тактова частота MCU

    // Ініціалізація таймера (16 МГц -> Prescaler 15 -> 1 МГц квант -> ARR 19999 -> 50 Гц ШІМ)
    if (!servo_tester_init(&tester, &TIM2_Hardware, system_clock)) {
        printf("Помилка ініціалізації таймера сервотестера!\n");
        return 1;
    }

    printf("Таймер успішно ініціалізовано: period=%u us (50 Hz), PSC=%u, ARR=%u\n",
           SERVO_PERIOD_US, (unsigned int)TIM2_Hardware.PSC, (unsigned int)TIM2_Hardware.ARR);

    // Запуск генерації ШІМ-сигналу
    servo_tester_start(&tester);
    printf("ШІМ-генерацію запущено.\n\n");

    // ЕТАП 1: Калібрування нейтрального положення для мікросхем AA5188/KC0032
    printf("--- Етап 1: Виставити нейтраль 1500 мкс (90 deg) ---\n");
    servo_tester_calibrate_neutral(&tester);
    printf("Встановлено імпульс: %u мкс (Кут: %u deg). Відкалібруйте потенціометр сервоприводу!\n",
           servo_tester_get_pulse_us(&tester), servo_tester_get_angle(&tester));
    delay_ms(1000);

    // ЕТАП 2: Покрокове сканування діапазону 0..180 градусів
    printf("\n--- Етап 2: Плавне розгортання кута (0 deg -> 180 deg) ---\n");
    for (uint8_t angle = 0; angle <= 180; angle += 30) {
        servo_tester_set_angle(&tester, angle);
        printf("Кут: %3u deg | Імпульс CCR1: %4u мкс\n",
               angle, servo_tester_get_pulse_us(&tester));
        delay_ms(200);
    }

    // ЕТАП 3: Перевірка динамічної реакції H-моста AA5188/KC0032 (стрибки позиції)
    printf("\n--- Етап 3: Випробування динамічного відгуку підсилювача ---\n");
    printf("Перехід на крайнє ліве положення (1000 мкс / 0 deg)...\n");
    servo_tester_set_pulse_us(&tester, 1000);
    delay_ms(500);

    printf("Перехід на крайнє праве положення (2000 мкс / 180 deg)...\n");
    servo_tester_set_pulse_us(&tester, 2000);
    delay_ms(500);

    printf("Повернення в нейтраль (1500 мкс / 90 deg)...\n");
    servo_tester_set_pulse_us(&tester, 1500);
    delay_ms(500);

    // ЕТАП 4: Перевірка захисного обмеження невалідних значень
    printf("\n--- Етап 4: Перевірка валідації та безпечних меж ---\n");
    printf("Спроба подачі недопустимого імпульсу 2500 мкс (вище межі)...\n");
    servo_tester_set_pulse_us(&tester, 2500);
    printf("Фактичне значення CCR1 після обрізання: %u мкс\n", servo_tester_get_pulse_us(&tester));

    printf("Спроба подачі недопустимого імпульсу 500 мкс (нижче межі)...\n");
    servo_tester_set_pulse_us(&tester, 500);
    printf("Фактичне значення CCR1 після обрізання: %u мкс\n", servo_tester_get_pulse_us(&tester));

    // Завершення тестування
    servo_tester_stop(&tester);
    printf("\nВипробування завершено. ШІМ вимкнено.\n");

    return 0;
}

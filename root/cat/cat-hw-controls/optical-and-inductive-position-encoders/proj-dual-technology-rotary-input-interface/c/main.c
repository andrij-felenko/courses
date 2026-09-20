#include <stdio.h>
#include "encoder_types.h"
#include "encoder_driver.h"

// Допоміжна функція виведення стану системи
static void print_system_status(uint32_t time_ms, const yoke_position_system_t *sys) {
    printf("[%5u мс] QEI: %6.2f° | RVDT: %6.2f° | Вихід: %6.2f° | Статус: ",
           time_ms,
           sys->qei.current_angle_deg,
           sys->rvdt.current_angle_deg,
           sys->valid_position_deg);

    switch (sys->comparator.status) {
        case COMPARE_OK:
            printf("НОРМА (OK)\n");
            break;
        case COMPARE_WARNING_DISCREPANCY:
            printf("ПОПЕРЕДЖЕННЯ (Розходження)\n");
            break;
        case COMPARE_ERROR_DISCREPANCY:
            printf("АВАРІЯ (Таймаут розходження)\n");
            break;
        case COMPARE_ERROR_HARDWARE:
            printf("АПАРАТНИЙ ЗБОЙ (RVDT Fault)\n");
            break;
    }
}

int main(void) {
    printf("=== Драйвер подвійного давача положення штурвала C (QEI + RVDT) ===\n\n");

    yoke_position_system_t yoke_sys;
    // Ініціалізація: QEI=4096 імпульсів, RVDT=20мВ/град, Макс. розходження=2.0°, Таймаут=100мс
    yoke_system_init(&yoke_sys, 4096, 20.0f, 2.0f, 100);

    uint32_t time_ms = 0;
    uint16_t adc_buffer[RVDT_DMA_BUFFER_SIZE];

    // 1. Нормальна синхронна робота (поворот штурвала на +10 градусів)
    printf("--- 1. Нормальний рух штурвала (узгоджені канали) ---\n");
    // QEI: 114 імпульси зі 4096 -> приблизно 10 градусів
    yoke_update_qei(&yoke_sys, 114, true);
    
    // RVDT: 1650 мВ + (10 град * 20 мВ/град) = 1850 мВ -> АЦП відлік ~ 2296
    for (int i = 0; i < RVDT_DMA_BUFFER_SIZE; ++i) {
        adc_buffer[i] = 2296;
    }
    yoke_update_rvdt(&yoke_sys, adc_buffer, RVDT_DMA_BUFFER_SIZE);
    
    yoke_process_cycle(&yoke_sys, time_ms);
    print_system_status(time_ms, &yoke_sys);

    // 2. Симуляція виникнення короткочасної розбіжності (пропуск імпульсу QEI)
    printf("\n--- 2. Виникнення розбіжності каналів (QEI відстає) ---\n");
    time_ms += 20;
    yoke_update_qei(&yoke_sys, 114, true); // Кут QEI = 10.0°
    
    // RVDT повертає кут 13.5° (ADC відлік ~ 2358) -> різниця 3.5° > 2.0°
    for (int i = 0; i < RVDT_DMA_BUFFER_SIZE; ++i) {
        adc_buffer[i] = 2358;
    }
    yoke_update_rvdt(&yoke_sys, adc_buffer, RVDT_DMA_BUFFER_SIZE);
    
    yoke_process_cycle(&yoke_sys, time_ms);
    print_system_status(time_ms, &yoke_sys);

    // 3. Перевищення таймауту розходження (понад 100 мс)
    printf("\n--- 3. Перевищення таймауту розходження (100 мс) ---\n");
    time_ms += 110;
    yoke_process_cycle(&yoke_sys, time_ms);
    print_system_status(time_ms, &yoke_sys);

    // 4. Усунення розсихронізації та відновлення роботи
    printf("\n--- 4. Синхронізація сигналів та виконання Reset ---\n");
    time_ms += 20;
    yoke_update_qei(&yoke_sys, 154, true); // QEI підтягнуто до 13.5°
    yoke_process_cycle(&yoke_sys, time_ms);
    print_system_status(time_ms, &yoke_sys);

    printf("Виклику процедури відновлення (yoke_reset_fault):\n");
    if (yoke_reset_fault(&yoke_sys)) {
        printf("Прапорець аварії скинуто успішно.\n");
    }
    yoke_process_cycle(&yoke_sys, time_ms);
    print_system_status(time_ms, &yoke_sys);

    printf("\n=== Тестування драйвера завершено успішно ===\n");
    return 0;
}

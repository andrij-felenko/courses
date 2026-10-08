#include <stdio.h>
#include <stdbool.h>
#include "../include/stm32_timer_hal.h"
#include "../include/encoder.h"

/* Симуляція регістрів апаратного таймера TIM2 в пам'яті */
static TIM_TypeDef g_tim2_hardware = {0};
#define TIM2 (&g_tim2_hardware)

/* Глобальний контекст енкодера для доступу з обробників переривань ISR */
static encoder_t g_encoder;

/**
 * @brief Обробник переривання оновлення таймера TIM2 (Update ISR)
 */
void TIM2_IRQHandler(void) {
    encoder_handle_overflow_isr(&g_encoder);
}

/**
 * @brief Обробник зовнішнього переривання EXTI0 для індексного сигналу Z
 */
void EXTI0_IRQHandler(void) {
    encoder_handle_index_z_isr(&g_encoder);
}

int main(void) {
    printf("=== Симуляція драйвера квадратурного енкодера STM32 ===\n\n");

    /* Конфігурація апаратного таймера STM32 у режимі x4 з фільтрацією завад */
    stm32_timer_config_t hal_cfg = {
        .timer = TIM2,
        .filter_ch1 = TIM_IC_FILTER_FDTS_N8, /* Фільтрація 8 тактів завад на входу A */
        .filter_ch2 = TIM_IC_FILTER_FDTS_N8, /* Фільтрація 8 тактів завад на входу B */
        .polarity_ch1 = TIM_ENCODER_POLARITY_RISING,
        .polarity_ch2 = TIM_ENCODER_POLARITY_RISING,
        .auto_reload = 0xFFFFU, /* 16-бітне перезавантаження */
        .exti_line = 1U << 0    /* EXTI Line 0 для індексного імпульсу Z */
    };

    /* Конфігурація драйвера енкодера */
    encoder_config_t enc_cfg = {
        .ppr = 1024,              /* 1024 імпульси/оборот -> 4096 відліків/оборот у режимі x4 */
        .gear_ratio = 1.0f,       /* Прямий привід без редуктора */
        .invert_direction = false,
        .hal_config = hal_cfg
    };

    /* Ініціалізація енкодера */
    if (!encoder_init(&g_encoder, &enc_cfg)) {
        printf("Помилка: не вдалося ініціалізувати енкодер!\n");
        return -1;
    }

    printf("Енкодер успішно ініціалізовано.\n");
    printf("Роздільна здатність: %u PPR (%u відліків/оборот у режимі x4)\n\n",
           enc_cfg.ppr, enc_cfg.ppr * 4U);

    /* Імітація обертання вала вгору (overflow 16-бітного лічильника) */
    printf("--- Імітація руху: обертання CW з переповненням лічильника ---\n");
    TIM2->CR1 &= ~TIM_CR1_DIR; /* DIR = 0 (Upcounting) */

    TIM2->CNT = 65530U;
    printf("Початковий CNT = %u, Raw Pos = %lld\n",
           TIM2->CNT, (long long)encoder_get_position_raw(&g_encoder));

    /* Імітуємо перехід через 65535 на 5 відліків вперід (overflow) */
    TIM2->CNT = 4U;
    TIM2->SR |= TIM_SR_UIF; /* Спрацював прапорець Update Interrupt */
    TIM2_IRQHandler();      /* Виклик ISR переривання */

    printf("Після переповнення: CNT = %u, Overflow Count = %d, Raw Pos = %lld\n",
           TIM2->CNT, g_encoder.overflow_count, (long long)encoder_get_position_raw(&g_encoder));

    /* Імітація проходження індексного імпульсу Z (EXTI ISR) */
    printf("\n--- Спрацював індексний імпульс Z (калібрування нуля) ---\n");
    EXTI0_IRQHandler();
    printf("Калібровано: %s | Zero Offset = %lld counts\n",
           g_encoder.is_calibrated ? "ТАК" : "НІ", (long long)g_encoder.zero_offset_counts);
    printf("Калібрована позиція = %lld counts, Кут = %.4f рад\n",
           (long long)encoder_get_position_calibrated(&g_encoder),
           encoder_get_angle_radians(&g_encoder));

    /* Імітація періодичного розрахунку кутової швидкості (наприклад, dt = 10 мс) */
    printf("\n--- Обчислення кутової швидкості (dt = 10 мс) ---\n");
    /* Зміщуємо позицію на 205 відліків за 0.01 с */
    TIM2->CNT = 209U;
    encoder_update_velocity(&g_encoder, 0.01f);

    printf("Приріст dN = 205 відліків за 10 мс\n");
    printf("Поточний напрямок: %s\n",
           g_encoder.current_direction == ENCODER_DIR_CW ? "CW (за стрілкою)" : "CCW");
    printf("Кутова швидкість w = %.2f рад/с\n", g_encoder.angular_velocity_rad_s);
    printf("Швидкість обертання = %.2f RPM\n", g_encoder.speed_rpm);

    return 0;
}

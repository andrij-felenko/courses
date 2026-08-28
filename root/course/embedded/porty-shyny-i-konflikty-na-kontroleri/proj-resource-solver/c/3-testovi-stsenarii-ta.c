#include <stdio.h>

int main(void) {
    HardwareResourceManager mgr;
    resource_manager_init(&mgr);

    // Сценарій 1: Коректна конфігурація з авторозв'язанням колізії DMA
    PinResource valid_quad_pins[] = {
        {"PA8",  1, 1, 2, 5, 7, 6, PROTO_DSHOT600}, // Motor 1 (TIM1_CH1, DMA2_S5, alt S7)
        {"PA9",  1, 2, 2, 2, 0xFF, 6, PROTO_DSHOT600}, // Motor 2 (TIM1_CH2, DMA2_S2)
        {"PA10", 1, 3, 2, 6, 0xFF, 6, PROTO_DSHOT600}, // Motor 3 (TIM1_CH3, DMA2_S6)
        {"PA11", 1, 4, 2, 4, 0xFF, 6, PROTO_DSHOT600}, // Motor 4 (TIM1_CH4, DMA2_S4)
        {"PB0",  3, 1, 1, 4, 0xFF, 5, PROTO_WS2812_LED},// LED Strip (TIM3_CH1, DMA1_S4)
        {"PA5",  0, 0, 2, 0, 0xFF, 3, PROTO_SPI_IMU},  // Gyro SPI1_RX (DMA2_S0)
        {"PA7",  0, 0, 2, 5, 3,    3, PROTO_SPI_IMU}   // Gyro SPI1_TX (DMA2_S5, конфліктує з M1!)
    };

    ValidationResult res = resource_manager_validate(&mgr, valid_quad_pins, 7);
    if (res == VALIDATION_OK) {
        printf("Тест 1 успішний: конфігурацію валідовано, усунуто колізій DMA: %u\n", 
               mgr.resolved_collisions_count);
    } else {
        printf("Тест 1 провалено з кодом помилки: %d\n", res);
    }

    // Сценарій 2: Фатальний таймерний конфлікт (Motor 5 на таймері LED-стрічки)
    HardwareResourceManager bad_mgr;
    resource_manager_init(&bad_mgr);

    PinResource invalid_pins[] = {
        {"PB0",  3, 1, 1, 4, 0xFF, 5, PROTO_WS2812_LED}, // LED Strip на TIM3_CH1
        {"PB1",  3, 4, 1, 2, 0xFF, 5, PROTO_DSHOT600},  // Motor 5 на TIM3_CH4 (КОНФЛІКТ!)
        {"PA5",  0, 0, 2, 0, 0xFF, 3, PROTO_SPI_IMU}
    };

    ValidationResult bad_res = resource_manager_validate(&bad_mgr, invalid_pins, 3);
    if (bad_res == ERR_TIMER_PROTOCOL_CONFLICT) {
        printf("Тест 2 успішний: таймерний конфлікт своєчасно заблоковано валідатором.\n");
    } else {
        printf("Тест 2 провалено: конфлікт не виявлено!\n");
    }

    return 0;
}

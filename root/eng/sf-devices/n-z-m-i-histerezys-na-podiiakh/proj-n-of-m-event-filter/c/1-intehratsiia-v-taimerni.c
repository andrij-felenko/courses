#include "main.h"
#include "event_filter.h"

/* Статичні екземпляри фільтрів для вхідних каналів */
static event_filter_fast32_t button_filter;
static event_filter_fast32_t sensor_filter;

void System_Filters_Init(void) {
    event_filter_config_t btn_cfg = {
        .m_window = 16,
        .n_on = 12,
        .n_off = 4,
        .max_dwell_samples = 0
    };
    event_filter_fast32_init(&button_filter, &btn_cfg, false);

    event_filter_config_t sns_cfg = {
        .m_window = 8,
        .n_on = 6,
        .n_off = 2,
        .max_dwell_samples = 5000 /* 5 секунд макс. активності */
    };
    event_filter_fast32_init(&sensor_filter, &sns_cfg, false);
}

/**
 * @brief Обробник переривання базового таймера TIM6 (частота 1 кГц)
 */
void TIM6_DAC_IRQHandler(void) {
    if (LL_TIM_IsActiveFlag_UPDATE(TIM6)) {
        LL_TIM_ClearFlag_UPDATE(TIM6);

        /* Зчитування фізичного рівня пінів з регістру IDR */
        bool raw_btn = LL_GPIO_IsInputPinSet(GPIOC, LL_GPIO_PIN_13) == 0; // Active-Low кнопка
        bool raw_sns = LL_GPIO_IsInputPinSet(GPIOA, LL_GPIO_PIN_0) != 0;  // Active-High оптичний датчик

        /* Оновлення станів фільтрів (виконується за 20 тактів) */
        event_filter_fast32_update(&button_filter, raw_btn);
        event_filter_fast32_update(&sensor_filter, raw_sns);
    }
}

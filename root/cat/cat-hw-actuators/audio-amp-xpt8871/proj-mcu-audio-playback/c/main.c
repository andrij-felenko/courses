#include "xpt8871.h"

/* Частота дискретизації аудіопотоку: 16 кГц */
#define SAMPLE_RATE_HZ      16000U

/* Апаратні дескриптори STM32 */
static DAC_HandleTypeDef hdac;
static TIM_HandleTypeDef htim6;

/* Екземпляр драйвера підсилювача */
static xpt8871_t amp;

/* 32-точкова таблиця синуса для апаратної генерації звукових тонів (значення 0..255) */
static const uint8_t SINE_LUT[32] = {
    128, 152, 176, 198, 218, 234, 245, 253,
    255, 253, 245, 234, 218, 198, 176, 152,
    128, 104,  80,  58,  38,  22,  11,   3,
      1,   3,  11,  22,  38,  58,  80, 104
};

/* Налаштування тактування системи (STM32F4, 84 МГц) */
static void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 8;
    RCC_OscInitStruct.PLL.PLLN = 336;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
    RCC_OscInitStruct.PLL.PLLQ = 7;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                                  RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}

/* Ініціалізація виводів GPIO: PB0 для SHDN підсилювача, PC13 для світлодіода активності */
static void GPIO_Init(void) {
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};

    /* Пін керування режимом сну XPT8871 (SHDN): вихід Push-Pull */
    gpio.Pin = GPIO_PIN_0;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_PULLDOWN;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &gpio);

    /* Індикаторний світлодіод для демонстрації неблокувальної роботи */
    gpio.Pin = GPIO_PIN_13;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &gpio);
}

/* Ініціалізація апаратного цифро-аналогового перетворювача (DAC1, канал 1 / PA4) */
static void DAC_Init(void) {
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_DAC_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_4;
    gpio.Mode = GPIO_MODE_ANALOG;
    gpio.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &gpio);

    hdac.Instance = DAC;
    HAL_DAC_Init(&hdac);

    DAC_ChannelConfTypeDef config = {0};
    config.DAC_Trigger = DAC_TRIGGER_NONE;
    config.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
    HAL_DAC_ConfigChannel(&hdac, &config, DAC_CHANNEL_1);
}

/*
 * Ініціалізація таймера TIM6 для генерації переривань частоти дискретизації (16 кГц).
 * Тактова частота шини APB1 таймерів = 84 МГц.
 * Prescaler = 0, Period = (84000000 / 16000) - 1 = 5249.
 */
static void TIM6_Init(uint32_t sample_rate) {
    __HAL_RCC_TIM6_CLK_ENABLE();

    htim6.Instance = TIM6;
    htim6.Init.Prescaler = 0;
    htim6.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim6.Init.Period = (84000000U / sample_rate) - 1U;
    htim6.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    HAL_TIM_Base_Init(&htim6);

    HAL_NVIC_SetPriority(TIM6_DAC_IRQn, 1, 0);
    HAL_NVIC_EnableIRQ(TIM6_DAC_IRQn);
}

/* Обробник апаратного переривання таймера TIM6 */
void TIM6_DAC_IRQHandler(void) {
    HAL_TIM_IRQHandler(&htim6);
}

/* Зворотний виклик HAL після переповнення періоду таймера: передача семпла в драйвер */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM6) {
        xpt8871_timer_isr(&amp);
    }
}

/*
 * Демонстраційна функція генерації та відтворення звукового сповіщення.
 * Синтезує двотональний сигнал (523 Гц та 659 Гц) тривалістю 400 мс (6400 семплів).
 * Наповнення кільцевого буфера відбувається порціями без затримки основного циклу.
 */
static void play_notification_melody(void) {
    const uint32_t total_samples = 6400U; /* 400 мс при 16 кГц */
    uint32_t generated = 0U;
    uint32_t phase_acc = 0U;

    /* Крок фазового акумулятора для 523 Гц та 659 Гц */
    const uint32_t step_tone1 = (523U * 32U * 1024U) / SAMPLE_RATE_HZ;
    const uint32_t step_tone2 = (659U * 32U * 1024U) / SAMPLE_RATE_HZ;

    uint8_t chunk[64];

    while (generated < total_samples) {
        /* Визначаємо, скільки семплів поміститься в кільцевий буфер драйвера */
        size_t free_space = xpt8871_get_free_space(&amp);
        size_t to_gen = sizeof(chunk);

        if (to_gen > free_space) {
            to_gen = free_space;
        }

        if (generated + to_gen > total_samples) {
            to_gen = total_samples - generated;
        }

        if (to_gen > 0U) {
            for (size_t i = 0U; i < to_gen; i++) {
                uint32_t current_idx = generated + i;
                uint32_t step = (current_idx < (total_samples / 2U)) ? step_tone1 : step_tone2;

                phase_acc += step;
                uint8_t lut_idx = (phase_acc >> 10) & 31U;
                chunk[i] = SINE_LUT[lut_idx];
            }

            /* Неблокувальний запис у кільцевий буфер */
            size_t written = xpt8871_write(&amp, chunk, to_gen);
            generated += written;
        }

        /* Фонова активність — блимання світлодіодом без переривання звуку */
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
        HAL_Delay(10);
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    GPIO_Init();
    DAC_Init();
    TIM6_Init(SAMPLE_RATE_HZ);

    /* Конфігурація драйвера XPT8871 */
    xpt8871_hw_config_t hw_config = {
        .shdn_port    = GPIOB,
        .shdn_pin     = GPIO_PIN_0,
        .hdac         = &hdac,
        .dac_channel  = DAC_CHANNEL_1,
        .htim         = &htim6
    };

    /* Ініціалізація: підсилювач залишається у стані сну (SHDN = LOW) */
    xpt8871_init(&amp, &hw_config, SAMPLE_RATE_HZ);

    while (1) {
        /* Відтворюємо звуковий сигнал */
        play_notification_melody();

        /*
         * Очікуємо завершення звучання залишку буфера та автоматичного
         * переходу XPT8871 у сплячий режим через idle-таймаут.
         * Головний потік не заблокований — світлодіод продовжує блимати.
         */
        while (xpt8871_is_playing(&amp)) {
            HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
            HAL_Delay(50);
        }

        /* Підсилювач спить (струм споживання < 1 мкА, немає фонового шипіння) */
        for (int i = 0; i < 30; i++) {
            HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
            HAL_Delay(100);
        }
    }
}

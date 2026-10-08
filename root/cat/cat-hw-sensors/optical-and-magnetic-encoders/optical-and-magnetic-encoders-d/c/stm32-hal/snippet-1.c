// Конфігурація таймера TIM2 у режимі квадратурного декодувальника (x4) на C
void Encoder_Init(TIM_HandleTypeDef *htim) {
    TIM_Encoder_InitTypeDef encoderConfig = {0};

    encoderConfig.EncoderMode = TIM_ENCODERMODE_TI12; // Режим x4 (обробка TI1 та TI2)
    encoderConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
    encoderConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
    encoderConfig.IC1Prescaler = TIM_ICPSC_DIV1;
    encoderConfig.IC1Filter = 0x05; // Апаратний цифровий фільтр від деренчання

    encoderConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
    encoderConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
    encoderConfig.IC2Prescaler = TIM_ICPSC_DIV1;
    encoderConfig.IC2Filter = 0x05;

    HAL_TIM_Encoder_Init(htim, &encoderConfig);
    HAL_TIM_Encoder_Start(htim, TIM_CHANNEL_ALL);
}

int32_t Encoder_GetPosition(TIM_HandleTypeDef *htim) {
    return (int32_t)__HAL_TIM_GET_COUNTER(htim);
}

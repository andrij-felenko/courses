// Той самий цикл у main(): прапорець від TIM2 задає момент, решта — після нього.
#define N_AVG  16                        // √16 = 4× тихіше; +2 «ефективні» біти
extern ADC_HandleTypeDef hadc1;          // канал давача налаштований у CubeMX, 12 біт

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_TIM2_Init();
    setup_sampler(1000);                 // fs = 1 кГц: надвибірка над повільним давачем

    while (1) {
        if (!tick) continue;             // ще не час знімка — не робимо НІЧОГО тут
        tick = false;

        uint32_t code = read_clean(&hadc1, N_AVG);   // чисте усереднене читання
        uint32_t mv   = code * vref_mv / 4095U;      // vref_mv — виміряне через VREFINT
        control_step(mv);                // готове число — регулятору (наступний крок модуля)
    }
}

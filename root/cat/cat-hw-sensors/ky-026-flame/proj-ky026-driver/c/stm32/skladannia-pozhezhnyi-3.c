/* Пороги в 12-бітних одиницях — перекалібровані під 0..4095, а не 0..1023. */
#define SEE_FIRE   800.0f      /* сума жару, з якої робот починає їхати на вогонь */
#define BURN_NEAR 2800.0f      /* сума, з якої вважаємо, що впритул → гасити */
#define BASE_SPD   140         /* базова швидкість руху вперед */
#define TURN_GAIN  0.6f        /* наскільки різко кермувати за різницею */

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init(); MX_DMA_Init(); MX_ADC1_Init(); MX_TIM2_Init();
    motors_init();
    HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_RESET);

    HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc_pair, 2);
    HAL_Delay(5);                              /* дай DMA принести перші числа */
    ir_l = adc_pair[0];                        /* старт середніх — з поточних значень */
    ir_r = adc_pair[1];

    while (1) {
        read_sensors();
        float sum  = ir_l + ir_r;              /* загальна близькість вогню */
        float diff = ir_l - ir_r;              /* >0 → жар зліва, <0 → справа */

        if (sum < SEE_FIRE) {                  /* вогню не видно — стій */
            HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_RESET);
            drive(0, 0);
        } else if (sum >= BURN_NEAR) {         /* впритул — стоп і дми */
            drive(0, 0);
            HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_SET);
        } else {                               /* бачимо вогонь — їдемо, підрулюючи */
            HAL_GPIO_WritePin(FAN_PORT, FAN_PIN, GPIO_PIN_RESET);
            int turn = (int)(TURN_GAIN * diff);
            drive(BASE_SPD - turn, BASE_SPD + turn);
        }
        HAL_Delay(20);                         /* ~50 Гц — досить для керма */
    }
}

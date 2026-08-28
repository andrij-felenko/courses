/* Бітові маски контролера тактування */
#define RCC_AHB1ENR_GPIOAEN   (1UL << 0)
#define RCC_APB1ENR_TIM6EN    (1UL << 4)

/* Бітові маски таймера TIM6 */
#define TIM_CR1_CEN           (1UL << 0)
#define TIM_CR1_URS           (1UL << 2)
#define TIM_SR_UIF            (1UL << 0)
#define TIM_EGR_UG            (1UL << 0)

/* Ініціалізація виводу PA5 (світлодіод) */
void gpio_pa5_init(void) {
    /* 1. Увімкнути тактування порту GPIOA на шині AHB1 */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    /* Коротке читання назад для очікування завершення шинної транзакції */
    (void)RCC->AHB1ENR;

    /* 2. Налаштувати пін 5 на вихід (MODER5 = 01) */
    GPIOA->MODER &= ~(3UL << (5 * 2));   /* Очистити біти 11:10 */
    GPIOA->MODER |=  (1UL << (5 * 2));   /* Встановити режим 01 (General purpose output) */

    /* 3. Тип виходу: Push-Pull (0 у біті 5 регістра OTYPER) */
    GPIOA->OTYPER &= ~(1UL << 5);

    /* 4. Швидкість фронту: Low speed (00 у бітах 11:10 OSPEEDR) */
    GPIOA->OSPEEDR &= ~(3UL << (5 * 2));

    /* 5. Без підтяжок: No pull-up, no pull-down (00 у бітах 11:10 PUPDR) */
    GPIOA->PUPDR &= ~(3UL << (5 * 2));
}

/* Атомарне керування станом виводу PA5 */
void gpio_pa5_set_high(void) {
    /* Запис 1 у біт 5 регістра BSRR вмикає вихід без зміни інших пінів */
    GPIOA->BSRR = (1UL << 5);
}

void gpio_pa5_set_low(void) {
    /* Запис 1 у біт (5 + 16) регістра BSRR скидає вихід в 0 */
    GPIOA->BSRR = (1UL << (5 + 16));
}

/* Ініціалізація таймера TIM6 для відліку мілісекунд (за тактової частоти шини APB1 = 16 МГц) */
void timer6_init_ms(void) {
    /* 1. Увімкнути тактування таймера TIM6 на шині APB1 */
    RCC->APB1ENR |= RCC_APB1ENR_TIM6EN;
    (void)RCC->APB1ENR;

    /* 2. Встановити дільник Prescaler: 16 000 000 / 16 000 = 1000 Гц (1 такт = 1 мс) */
    TIM6->PSC = 16000UL - 1UL;

    /* 3. Встановити максимальний період (Auto-Reload) */
    TIM6->ARR = 0xFFFFUL;

    /* 4. Згенерувати подію оновлення для негайного завантаження значення дільника у тіньовий регістр */
    TIM6->EGR |= TIM_EGR_UG;

    /* 5. Очистити прапорець оновлення, піднятий примусовою подією UG */
    TIM6->SR &= ~TIM_SR_UIF;

    /* 6. Запустити таймер (Counter Enable) */
    TIM6->CR1 |= TIM_CR1_CEN;
}

/* Блокуюча мілісекундна затримка з коректною обробкою переповнення лічильника */
void delay_ms(uint16_t ms) {
    uint16_t start = (uint16_t)TIM6->CNT;
    while ((uint16_t)(TIM6->CNT - start) < ms) {
        /* Циклічна арифметика беззнакових чисел гарантує правильний відлік навіть при переході через 0xFFFF */
    }
}

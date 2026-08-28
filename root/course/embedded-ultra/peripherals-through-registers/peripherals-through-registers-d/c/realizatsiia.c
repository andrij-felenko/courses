#include <stdint.h>
#include <stdbool.h>

/* Адресна карта мікроконтролера */
#define PERIPH_BASE       (0x40000000UL)
#define APB1PERIPH_BASE   (PERIPH_BASE)
#define AHB1PERIPH_BASE   (PERIPH_BASE + 0x00020000UL)

#define RCC_BASE          (AHB1PERIPH_BASE + 0x3800UL)
#define GPIOA_BASE        (AHB1PERIPH_BASE + 0x0000UL)
#define TIM6_BASE         (APB1PERIPH_BASE + 0x1000UL)

/* Структури регістрів периферії */
typedef struct {
    volatile uint32_t CR;
    volatile uint32_t PLLCFGR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t AHB1RSTR;
    volatile uint32_t AHB2RSTR;
    volatile uint32_t AHB3RSTR;
    uint32_t          RESERVED0;
    volatile uint32_t APB1RSTR;
    volatile uint32_t APB2RSTR;
    uint32_t          RESERVED1[2];
    volatile uint32_t AHB1ENR;
    volatile uint32_t AHB2ENR;
    volatile uint32_t AHB3ENR;
    uint32_t          RESERVED2;
    volatile uint32_t APB1ENR;
    volatile uint32_t APB2ENR;
} RCC_TypeDef;

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} GPIO_TypeDef;

typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    uint32_t          RESERVED0;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    uint32_t          RESERVED1[3];
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
} TIM_TypeDef;

#define RCC    ((RCC_TypeDef *)RCC_BASE)
#define GPIOA  ((GPIO_TypeDef *)GPIOA_BASE)
#define TIM6   ((TIM_TypeDef *)TIM6_BASE)

/* Ініціалізація виводу PA5 */
void led_gpio_init(void) {
    /* 1. Увімкнути тактування порту GPIOA на шині AHB1 (біт 0) */
    RCC->AHB1ENR |= (1UL << 0);
    (void)RCC->AHB1ENR; /* Захист від затримки шини */

    /* 2. Налаштувати PA5 як вихід: біти MODER5[1:0] = 01 */
    GPIOA->MODER &= ~(3UL << (5 * 2)); /* Очистити старий режим */
    GPIOA->MODER |=  (1UL << (5 * 2)); /* Встановити 01 (Output) */

    /* 3. Тип виходу: Push-Pull (біт 5 = 0) */
    GPIOA->OTYPER &= ~(1UL << 5);

    /* 4. Швидкість фронту: Low Speed (біти OSPEEDR5[1:0] = 00) */
    GPIOA->OSPEEDR &= ~(3UL << (5 * 2));

    /* 5. Без підтяжок: No Pull-up/down (біти PUPDR5[1:0] = 00) */
    GPIOA->PUPDR &= ~(3UL << (5 * 2));
}

/* Ініціалізація базового таймера TIM6 на відлік мілісекунд (тактова APB1 = 16 МГц) */
void timer6_init(void) {
    /* 1. Подати тактування на таймер TIM6 (шина APB1, біт 4) */
    RCC->APB1ENR |= (1UL << 4);
    (void)RCC->APB1ENR;

    /* 2. Дільник Prescaler: 16 МГц / 16000 = 1 кГц (1 такт = 1 мс) */
    TIM6->PSC = 16000UL - 1UL;

    /* 3. Межа автоперезавантаження (Auto-Reload) */
    TIM6->ARR = 0xFFFFUL;

    /* 4. Примусове оновлення для завантаження значення PSC у тіньовий регістр */
    TIM6->EGR |= (1UL << 0);

    /* 5. Очищення прапорця оновлення (UIF) */
    TIM6->SR &= ~(1UL << 0);

    /* 6. Запуск лічильника (CEN = 1) */
    TIM6->CR1 |= (1UL << 0);
}

/* Блокуюча мілісекундна затримка з обробкою переповнення лічильника */
void delay_ms(uint16_t ms) {
    uint16_t start = (uint16_t)TIM6->CNT;
    while ((uint16_t)(TIM6->CNT - start) < ms) {
        /* Опитування апаратного лічильника з циклічною різницею */
    }
}

int main(void) {
    led_gpio_init();
    timer6_init();

    while (1) {
        /* Атомарне ввімкнення світлодіода (PA5 = 1) */
        GPIOA->BSRR = (1UL << 5);
        delay_ms(500);

        /* Атомарне вимкнення світлодіода (PA5 = 0) */
        GPIOA->BSRR = (1UL << (5 + 16));
        delay_ms(500);
    }
}

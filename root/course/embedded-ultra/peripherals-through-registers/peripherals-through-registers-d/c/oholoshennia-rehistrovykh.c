/* Оголошення структури регістрів GPIO мовою C */
typedef struct {
    volatile uint32_t MODER;    /* Зміщення +0x00: Режим роботи пінів */
    volatile uint32_t OTYPER;   /* Зміщення +0x04: Тип виходу */
    volatile uint32_t OSPEEDR;  /* Зміщення +0x08: Швидкість наростання фронту */
    volatile uint32_t PUPDR;    /* Зміщення +0x0C: Підтягуючі резистори */
    volatile uint32_t IDR;      /* Зміщення +0x10: Вхідні дані */
    volatile uint32_t ODR;      /* Зміщення +0x14: Вихідні дані */
    volatile uint32_t BSRR;     /* Зміщення +0x18: Атомарне керування бітами */
    volatile uint32_t LCKR;     /* Зміщення +0x1C: Блокування конфігурації */
    volatile uint32_t AFR[2];   /* Зміщення +0x20: Альтернативні функції (2 слова) */
} GPIO_TypeDef;

#define GPIOA_BASE    (0x40020000UL)
#define GPIOA         ((GPIO_TypeDef *)GPIOA_BASE)

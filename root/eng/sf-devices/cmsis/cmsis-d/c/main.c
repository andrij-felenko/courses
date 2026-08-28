typedef struct {
    volatile uint32_t MODER;    // 0x00  режим виводів
    volatile uint32_t OTYPER;   // 0x04
    volatile uint32_t OSPEEDR;  // 0x08
    volatile uint32_t PUPDR;    // 0x0C
    volatile uint32_t IDR;      // 0x10  вхідні дані
    volatile uint32_t ODR;      // 0x14  вихідні дані
    volatile uint32_t BSRR;     // 0x18  атомарний set/reset
} GPIO_TypeDef;

#define GPIOA  ((GPIO_TypeDef*) 0x40020000)

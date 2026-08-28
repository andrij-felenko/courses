typedef struct {
    volatile uint32_t MODER;   // зсув 0x00 — режим ніжок
    volatile uint32_t OTYPER;  // зсув 0x04
    volatile uint32_t OSPEEDR; // зсув 0x08
    volatile uint32_t PUPDR;   // зсув 0x0C
    volatile uint32_t IDR;     // зсув 0x10 — вхідні дані
    volatile uint32_t ODR;     // зсув 0x14 — вихідні дані
    volatile uint32_t BSRR;    // зсув 0x18 — атомарна установка/скидання
    // ...
} GPIO_TypeDef;

#define GPIOA  ((GPIO_TypeDef *) 0x40020000)   // базова адреса порту A

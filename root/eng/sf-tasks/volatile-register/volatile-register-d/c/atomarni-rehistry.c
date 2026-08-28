// Атомарне перемикання ніжки GPIO без операцій RMW і без блокування переривань
typedef struct {
    volatile uint32_t MODER;   // Режим виводів
    volatile uint32_t OTYPER;  // Тип виходу
    volatile uint32_t OSPEEDR; // Швидкість
    volatile uint32_t PUPDR;   // Підтяжка
    volatile uint32_t IDR;     // Вхідні дані (RO)
    volatile uint32_t ODR;     // Вихідні дані (RW - небезпечно для RMW!)
    volatile uint32_t BSRR;    // Атомарне встановлення/скидання (Write-Only)
} GPIO_TypeDef;

#define GPIOA ((GPIO_TypeDef *)0x40020000UL)

void set_pin_5_high(void) {
    // Запис 1 у молодші 16 біт BSRR встановлює пін 5 у логічну 1
    GPIOA->BSRR = (1U << 5); // Одиночна атомарна інструкція STR
}

void set_pin_5_low(void) {
    // Запис 1 у старші 16 біт BSRR скидає пін 5 у логічний 0
    GPIOA->BSRR = (1U << (5 + 16)); // Одиночна атомарна інструкція STR
}

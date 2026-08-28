#include <stdint.h>
#include <stdbool.h>

typedef struct {
    volatile uint32_t MODER;    /* 0x00  режим кожного виводу, 2 біти на вивід */
    volatile uint32_t OTYPER;   /* 0x04  push-pull / відкритий стік            */
    volatile uint32_t OSPEEDR;  /* 0x08  швидкість фронту                      */
    volatile uint32_t PUPDR;    /* 0x0C  підтяжки                              */
    volatile uint32_t IDR;      /* 0x10  вхідні дані (тільки читання)          */
    volatile uint32_t ODR;      /* 0x14  вихідні дані                          */
    volatile uint32_t BSRR;     /* 0x18  атомарний set/reset                   */
    volatile uint32_t LCKR;     /* 0x1C  замок конфігурації                    */
    volatile uint32_t AFR[2];   /* 0x20–0x24  альтернативні функції            */
} GPIO_TypeDef;

#define GPIOA  ((GPIO_TypeDef *) 0x40020000u)
#define GPIOB  ((GPIO_TypeDef *) 0x40020400u)
#define GPIOC  ((GPIO_TypeDef *) 0x40020800u)

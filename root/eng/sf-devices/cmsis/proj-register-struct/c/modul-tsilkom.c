#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "cmsis_gcc.h"   /* __disable_irq / __get_PRIMASK / __set_PRIMASK */

typedef struct {
    volatile uint32_t MODER, OTYPER, OSPEEDR, PUPDR;
    volatile uint32_t IDR;                /* лише читання за призначенням */
    volatile uint32_t ODR, BSRR, LCKR;
    volatile uint32_t AFR[2];
} GPIO_TypeDef;

_Static_assert(offsetof(GPIO_TypeDef, IDR)  == 0x10, "GPIO: IDR зсунуто");
_Static_assert(offsetof(GPIO_TypeDef, BSRR) == 0x18, "GPIO: BSRR зсунуто");
_Static_assert(sizeof(GPIO_TypeDef)         == 0x28, "GPIO: розмір блоку не той");

typedef struct {
    volatile uint32_t CR, PLLCFGR, CFGR, CIR;
    volatile uint32_t AHB1RSTR, AHB2RSTR, AHB3RSTR;
    uint32_t          RESERVED0;          /* 0x1C */
    volatile uint32_t APB1RSTR, APB2RSTR;
    uint32_t          RESERVED1[2];       /* 0x28–0x2C */
    volatile uint32_t AHB1ENR;            /* 0x30 */
} RCC_TypeDef;

_Static_assert(offsetof(RCC_TypeDef, AHB1ENR) == 0x30, "RCC: AHB1ENR зсунуто");

#define GPIOA  ((GPIO_TypeDef *) 0x40020000u)
#define GPIOC  ((GPIO_TypeDef *) 0x40020800u)
#define RCC    ((RCC_TypeDef  *) 0x40023800u)

#define MODE_OUTPUT  1u

static inline void rcc_ahb1_enable(uint32_t mask)
{
    RCC->AHB1ENR |= mask;
    (void) RCC->AHB1ENR;                  /* читання-назад замість «двох тактів» */
}

static void gpio_mode(GPIO_TypeDef *port, unsigned pin, uint32_t mode)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();                                    /* MODER не має атомарного дублера */
    port->MODER = (port->MODER & ~(3u << (pin * 2))) | (mode << (pin * 2));
    __set_PRIMASK(primask);
}

static inline void gpio_write(GPIO_TypeDef *port, unsigned pin, bool on)
{
    port->BSRR = on ? (1u << pin) : (1u << (pin + 16));  /* одна транзакція */
}

static inline bool gpio_read(const GPIO_TypeDef *port, unsigned pin)
{
    return (port->IDR >> pin) & 1u;
}

int main(void)
{
    rcc_ahb1_enable((1u << 0) | (1u << 2));   /* такт GPIOA і GPIOC + читання-назад */
    gpio_mode(GPIOA, 5, MODE_OUTPUT);

    for (;;) {
        gpio_write(GPIOA, 5, gpio_read(GPIOC, 13));
    }
}

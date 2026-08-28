/* Базова структура генерується один раз для всієї групи USART */
typedef struct {
    __IO uint32_t SR;    /* 0x00: Status register */
    __IO uint32_t DR;    /* 0x04: Data register */
    __IO uint32_t BRR;   /* 0x08: Baud rate register */
    __IO uint32_t CR1;   /* 0x0C: Control register 1 */
    __IO uint32_t CR2;   /* 0x10: Control register 2 */
    __IO uint32_t CR3;   /* 0x14: Control register 3 */
    __IO uint32_t GTPR;  /* 0x18: Guard time and prescaler register */
} USART_TypeDef;

#define USART1_BASE  (0x40013800UL)
#define USART2_BASE  (0x40004400UL)

#define USART1       ((USART_TypeDef *) USART1_BASE)
#define USART2       ((USART_TypeDef *) USART2_BASE)

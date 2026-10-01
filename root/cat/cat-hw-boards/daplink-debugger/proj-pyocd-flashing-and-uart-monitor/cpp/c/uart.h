#ifndef UART_H
#define UART_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структурний опис регістрів периферійного модуля USART у мові C.
 */
typedef struct {
    volatile uint32_t SR;   /**< Регістр стану */
    volatile uint32_t DR;   /**< Регістр даних */
    volatile uint32_t BRR;  /**< Регістр конфігурації швидкості */
    volatile uint32_t CR1;  /**< Регістр керування 1 */
    volatile uint32_t CR2;  /**< Регістр керування 2 */
    volatile uint32_t CR3;  /**< Регістр керування 3 */
    volatile uint32_t GTPR; /**< Регістр захисного часу */
} USART_Registers_t;

/**
 * @brief Ініціалізація периферії UART у процедурному стилі.
 * 
 * @param usart Вказівник на структуру регістрів USART
 * @param pclk_freq Частота тактування шини периферії у Гц
 * @param baud_rate Бажана швидкість передачі в бодах
 */
void uart_init(USART_Registers_t* usart, uint32_t pclk_freq, uint32_t baud_rate);

/**
 * @brief Відправка одного байта (символу) через послідовний порт.
 * 
 * @param usart Вказівник на модуль USART
 * @param ch Символ для відправки
 */
void uart_write_char(USART_Registers_t* usart, char ch);

/**
 * @brief Відправка нуль-термінованого текстового рядка.
 * 
 * @param usart Вказівник на модуль USART
 * @param str Вказівник на C-рядок
 */
void uart_write_string(USART_Registers_t* usart, const char* str);

/**
 * @brief Відправка рядка з автоматичним додаванням переведення рядка (\r\n).
 * 
 * @param usart Вказівник на модуль USART
 * @param str Текстове повідомлення для логування
 */
void uart_println(USART_Registers_t* usart, const char* str);

/**
 * @brief Очікування завершення передачі останнього кадру (прапорець TC).
 * 
 * @param usart Вказівник на модуль USART
 */
void uart_flush(USART_Registers_t* usart);

#ifdef __cplusplus
}
#endif

#endif /* UART_H */

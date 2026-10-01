#ifndef SYSTEM_INIT_H
#define SYSTEM_INIT_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file system_init.h
 * @brief Заголовний файл модуля системної ініціалізації з оголошеннями функцій
 *        конфігурації периферії STM32F103 та налаштування зсуву VTOR.
 */

/* Адреса Flash-пам'яті та зміщення VTOR за замовчуванням (16 Кб для bootloader) */
#define FLASH_BASE_ADDR        0x08000000UL
#define BOOTLOADER_VTOR_OFFSET 0x00004000UL

/**
 * @brief Налаштування зсуву векторної таблиці переривань SCB->VTOR.
 * 
 * Необхідно для коректної обробки переривань під час запуску прошивки
 * через завантажувач (bootloader).
 * 
 * @param offset Зсув адреси від початку Flash-пам'яті в байтах.
 */
void system_vtor_config(uint32_t offset);

/**
 * @brief Конфігурація системи тактування RCC для роботи на частоті 72 МГц.
 * 
 * Налаштовує зовнішній кварцовий резонатор (HSE 8 МГц), множник PLL (x9)
 * та дільники шин AHB, APB1, APB2.
 */
void system_clock_config(void);

/**
 * @brief Ініціалізація портів введення-виведення GPIO для SWD та CDC UART.
 * 
 * Налаштовує тактування портів GPIOA, GPIOB, GPIOC та альтернативних функцій (AFIO).
 */
void system_gpio_config(void);

/**
 * @brief Налаштування контролера переривань NVIC для модулів периферії.
 * 
 * Встановлює пріоритети переривань для USART та системного таймера.
 */
void system_nvic_config(void);

/**
 * @brief Комплексна ініціалізація всіх систем мікроконтролера STM32F103.
 * 
 * Послідовно викликає VTOR, RCC, GPIO та NVIC конфігуратори.
 */
void system_init_all(void);

#endif /* SYSTEM_INIT_H */

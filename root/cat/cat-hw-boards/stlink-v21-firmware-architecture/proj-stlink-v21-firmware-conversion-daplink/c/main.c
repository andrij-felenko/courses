#include <stdio.h>
#include "vtor_relocate.h"

/**
 * @file main.c
 * @brief Точка входу: перевірка конфігурації картки пам'яті, верифікація та запуск завантажувача DAPLink.
 */

int main(void) {
    vtor_config_t config;
    daplink_header_t header;
    vtor_status_t status;

    printf("Ініціалізація модуля релокації векторів ST-Link V2.1...\n");

    /* 1. Налаштування карти пам'яті мікроконтролера */
    status = vtor_init_default_config(&config);
    if (status != VTOR_SUCCESS) {
        printf("Помилка ініціалізації конфігурації пам'яті: %d\n", status);
        return (int)status;
    }

    printf("Конфігурація Flash: Bootloader [0x%08X], DAPLink [0x%08X]\n",
           (unsigned int)config.bootloader_base_addr,
           (unsigned int)config.app_base_addr);

    /* 2. Перевірка цільової таблиці векторів завантажувача DAPLink */
    uint32_t target_vector_addr = config.app_base_addr;
    status = vtor_verify_header(target_vector_addr, &config, &header);

    if (status != VTOR_SUCCESS) {
        printf("Перевірка векторів за адресою 0x%08X завершилася помилкою: %d\n",
               (unsigned int)target_vector_addr, status);
        
        /* Спроба використати базову адресу Bootloader як резервний варіант */
        printf("Спроба верифікації базового Bootloader (0x%08X)...\n",
               (unsigned int)config.bootloader_base_addr);
        
        target_vector_addr = config.bootloader_base_addr;
        status = vtor_verify_header(target_vector_addr, &config, &header);
        
        if (status != VTOR_SUCCESS) {
            printf("Критична помилка: валідну таблицю векторів не знайдено!\n");
            return (int)status;
        }
    }

    printf("Знайдено валідні вектори:\n");
    printf(" - Початковий MSP: 0x%08X\n", (unsigned int)header.initial_msp);
    printf(" - Reset Handler:  0x%08X\n", (unsigned int)header.reset_handler_addr);

    printf("Виконання вимкнення NVIC, оновлення SCB->VTOR та перехід...\n");

    /* 3. Зсув VTOR, підготовка процесора та здійснення переходу */
    status = vtor_jump_to_bootloader(target_vector_addr, &config);

    /* Код нижче виконується лише у випадку помилки під час передачі керування */
    printf("Помилка виконання переходу до завантажувача: %d\n", status);
    return (int)status;
}

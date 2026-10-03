#include "vtor_relocate.h"

/**
 * @file vtor_relocate.c
 * @brief Низькорівнева реалізація вимкнення переривань, налаштування VTOR, MSP та переходу до DAPLink.
 */

/* Допоміжні внутрішні функції для ассемблерних інструкцій Cortex-M */

/**
 * @brief Встановлює значення Main Stack Pointer (MSP).
 */
static inline void set_msp(uint32_t top_of_stack) {
    __asm__ volatile (
        "msr msp, %0 \n\t"
        "isb         \n\t"
        :
        : "r" (top_of_stack)
        : "memory"
    );
}

/**
 * @brief Глобально вимикає масковані переривання (інструкція cpsid i).
 */
static inline void disable_global_irq(void) {
    __asm__ volatile ("cpsid i" : : : "memory");
}

/**
 * @brief Виконує бар'єри синхронізації даних та інструкцій.
 */
static inline void memory_barrier(void) {
    __asm__ volatile (
        "dsb 0xF \n\t"
        "isb 0xF \n\t"
        :
        :
        : "memory"
    );
}

vtor_status_t vtor_init_default_config(vtor_config_t *config) {
    if (config == NULL) {
        return VTOR_ERR_NULL_ARG;
    }

    config->bootloader_base_addr = STLINK_V21_BOOT_BASE;
    config->app_base_addr        = DAPLINK_APP_BASE;
    config->flash_end_addr       = STLINK_V21_FLASH_BASE + (128UL * 1024UL); /* 128 КБ Flash */
    config->sram_start_addr      = STLINK_V21_SRAM_BASE;
    config->sram_end_addr        = STLINK_V21_SRAM_END;

    return VTOR_SUCCESS;
}

vtor_status_t vtor_verify_header(uint32_t vector_table_addr, 
                                 const vtor_config_t *config, 
                                 daplink_header_t *header) {
    if (config == NULL || header == NULL) {
        return VTOR_ERR_NULL_ARG;
    }

    /* 1. Перевірка вирівнювання адреси векторів на 128 байтів */
    if ((vector_table_addr & (VTOR_ALIGNMENT_BYTES - 1UL)) != 0UL) {
        return VTOR_ERR_BAD_ALIGNMENT;
    }

    /* 2. Зчитання початкового MSP та Reset Handler з Flash */
    const volatile uint32_t *vector_ptr = (const volatile uint32_t *)vector_table_addr;
    header->initial_msp = vector_ptr[0];
    header->reset_handler_addr = vector_ptr[1];

    /* 3. Перевірка корректності MSP: має вказувати в межі SRAM */
    if (header->initial_msp < config->sram_start_addr || 
        header->initial_msp > config->sram_end_addr) {
        return VTOR_ERR_INVALID_MSP;
    }

    /* 4. Перевірка адреси Reset Handler: наявність Thumb-біта (біт 0 == 1) */
    if ((header->reset_handler_addr & 1UL) == 0UL) {
        return VTOR_ERR_INVALID_RESET;
    }

    /* 5. Перевірка фізичних меж адреси скидання у Flash */
    uint32_t raw_reset_addr = header->reset_handler_addr & ~1UL;
    if (raw_reset_addr < config->bootloader_base_addr || 
        raw_reset_addr >= config->flash_end_addr) {
        return VTOR_ERR_OUT_OF_BOUNDS;
    }

    return VTOR_SUCCESS;
}

void vtor_disable_interrupts_and_systick(void) {
    /* 1. Глобальне блокування системних переривань */
    disable_global_irq();

    /* 2. Зупинка та скидання регістрів таймера SysTick */
    SYSTICK_REG->CTRL = 0UL;
    SYSTICK_REG->LOAD = 0UL;
    SYSTICK_REG->VAL  = 0UL;

    /* 3. Деініціалізація векторів NVIC: вимкнення та очищення статусів очікування */
    for (size_t i = 0; i < 8; i++) {
        NVIC_REG->ICER[i] = 0xFFFFFFFFUL; /* Disable interrupts */
        NVIC_REG->ICPR[i] = 0xFFFFFFFFUL; /* Clear pending flags */
    }

    memory_barrier();
}

vtor_status_t vtor_set_offset(uint32_t vector_table_addr) {
    /* Перевірка відповідності адреси масці регістра SCB->VTOR */
    if ((vector_table_addr & ~VTOR_ALIGNMENT_MASK) != 0UL) {
        return VTOR_ERR_BAD_ALIGNMENT;
    }

    /* Оновлення регістра зсуву таблиці векторів */
    SCB_REG->VTOR = (vector_table_addr & VTOR_ALIGNMENT_MASK);

    /* Бар'єр для гарантованого оновлення конфігурації ядра */
    memory_barrier();

    return VTOR_SUCCESS;
}

vtor_status_t vtor_jump_to_bootloader(uint32_t vector_table_addr, 
                                      const vtor_config_t *config) {
    daplink_header_t header;
    vtor_status_t status;

    /* 1. Валідація таблиці векторів перед передачею керування */
    status = vtor_verify_header(vector_table_addr, config, &header);
    if (status != VTOR_SUCCESS) {
        return status;
    }

    /* 2. Вимкнення периферичних та системних переривань */
    vtor_disable_interrupts_and_systick();

    /* 3. Релокація регістра VTOR на таблицю векторів цільової прошивки */
    status = vtor_set_offset(vector_table_addr);
    if (status != VTOR_SUCCESS) {
        return status;
    }

    /* 4. Формування вказівника на точку входу завантажувача DAPLink */
    bootloader_jump_t jump_to_reset = (bootloader_jump_t)header.reset_handler_addr;

    /* 5. Налаштування Main Stack Pointer (MSP) цільової прошивки */
    set_msp(header.initial_msp);

    /* 6. Здійснення передачі керування (перехід на Reset Handler) */
    jump_to_reset();

    /* У разі успішного переходу точка виклику недосяжна */
    return VTOR_SUCCESS;
}

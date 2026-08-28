#ifndef MPU_ISOLATOR_H
#define MPU_ISOLATOR_H

#include "mpu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Кількість слотів регіонів для задач */
#define MPU_TASK_STACK_REGION       (5U)
#define MPU_TASK_GUARD_REGION       (6U)
#define MPU_TASK_PRIVATE_REGION     (7U)

/* Конфігурація задачі для реєстрації в ізоляторі */
typedef struct {
    uint32_t task_id;
    uint32_t stack_base;       /* Базова адреса стека (найнижча адреса буфера) */
    uint32_t stack_size;       /* Повний розмір стекового буфера в байтах */
    uint32_t guard_size;       /* Розмір захисної смуги в байтах (наприклад, 32 або 64) */
    uint32_t private_data_base;/* Базова адреса виділеної пам'яті задачі */
    uint32_t private_data_size;/* Розмір приватних даних */
} mpu_task_isolation_desc_t;

/* Callback-функція користувача при виявленні порушення прав */
typedef void (*mpu_fault_callback_t)(const mpu_fault_report_t *report);

/**
 * @brief Ініціалізація апаратного блоку MPU та активація винятку MemManage.
 * @param arch Архітектурний профіль (PMSAv7 або PMSAv8).
 * @param use_priv_default Дозволити фонову карту пам'яті для привілейованого режиму.
 * @return 0 при успіху, негативний код при помилці або відсутності MPU.
 */
int32_t mpu_isolator_init(mpu_arch_t arch, bool use_priv_default);

/**
 * @brief Конфігурація та активація статичного регіону пам'яті.
 * @param config Вказівник на структуру налаштувань регіону.
 * @return 0 при успіху, негативний код при некоректних параметрах.
 */
int32_t mpu_configure_region(const mpu_region_config_t *config);

/**
 * @brief Вимкнення конкретного регіону MPU.
 * @param region_number Номер слота регіону.
 * @return 0 при успіху, негативний код при виході за межі підтримуваних регіонів.
 */
int32_t mpu_disable_region(uint8_t region_number);

/**
 * @brief Швидке перемикання захищеного контексту під час зміни активної задачі RTOS.
 * @param task_desc Опис ізоляції цільової задачі, що запускається.
 * @note Викликається всередині PendSV або планувальника задач.
 */
void mpu_switch_task_context(const mpu_task_isolation_desc_t *task_desc);

/**
 * @brief Перевірка валідності буфера, переданого у системний виклик (Confused Deputy Prevention).
 * @param buffer Вказівник на початок буфера даних.
 * @param length Розмір буфера в байтах.
 * @param write_access True якщо системний виклик записуватиме у буфер, False для читання.
 * @return true якщо буфер повністю належить дозволеному простору задачі, інакше false.
 */
bool mpu_validate_buffer(const void *buffer, size_t length, bool write_access);

/**
 * @brief Реєстрація користувацького обробника аварійного порушення пам'яті.
 * @param callback Функція зворотного виклику.
 */
void mpu_register_fault_callback(mpu_fault_callback_t callback);

/**
 * @brief Низькорівневий обробник C для розбору стек-фрейму винятку MemManage.
 * @param stack_frame Вказівник на апаратно збережені регістри на поточному стеку.
 * @param exc_return Значення регістру зв'язку LR при вході у виняток.
 */
void mpu_memmanage_c_handler(mpu_fault_stack_frame_t *stack_frame, uint32_t exc_return);

#ifdef __cplusplus
}
#endif

#endif /* MPU_ISOLATOR_H */

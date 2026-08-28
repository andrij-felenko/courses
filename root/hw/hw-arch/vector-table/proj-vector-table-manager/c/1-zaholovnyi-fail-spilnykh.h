#ifndef VECTOR_TABLE_TYPES_H
#define VECTOR_TABLE_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Кількість стандартизованих системних винятків Cortex-M */
#define CORTEX_M_SYS_EXCEPTIONS_COUNT   16U

/** Максимальна кількість підтримуваних периферійних ліній IRQ */
#define CORTEX_M_MAX_IRQ_COUNT          128U

/** Повний розмір таблиці векторів у кількості 32-бітних слів */
#define VECTOR_TABLE_TOTAL_SLOTS        (CORTEX_M_SYS_EXCEPTIONS_COUNT + CORTEX_M_MAX_IRQ_COUNT)

/** Вимога до вирівнювання таблиці векторів у байтах (найближчий ступінь двійки) */
#define VECTOR_TABLE_ALIGNMENT_BYTES    1024U

/** Номер виділеного регіону MPU для захисту таблиці векторів */
#define VTM_MPU_REGION_NUMBER           7U

/** Тип покажчика на функцію обробника переривання */
typedef void (*isr_vector_t)(void);

/** Коди результатів операцій менеджера векторів */
typedef enum {
    VTM_STATUS_OK = 0,
    VTM_STATUS_ERROR_NOT_INITIALIZED,
    VTM_STATUS_ERROR_ALREADY_INITIALIZED,
    VTM_STATUS_ERROR_NULL_PTR,
    VTM_STATUS_ERROR_ALIGNMENT,
    VTM_STATUS_ERROR_INVALID_IRQ_NUM,
    VTM_STATUS_ERROR_INVALID_THUMB_BIT,
    VTM_STATUS_ERROR_MPU_CONFIG,
    VTM_STATUS_ERROR_BUS_FAULT
} vtm_status_t;

/** Апаратний стек-фрейм винятку ARM Cortex-M */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
} exception_stack_frame_t;

/** Розширений звіт про апаратну відмову HardFault */
typedef struct {
    exception_stack_frame_t frame;
    uint32_t exc_return_code;
    uint32_t hfsr;
    uint32_t cfsr;
    uint32_t bfar;
    uint32_t mmar;
    uint32_t afsr;
    bool bfar_valid;
    bool mmar_valid;
    bool is_psp_active;
    uint32_t crash_timestamp;
} hardfault_crash_report_t;

#ifdef __cplusplus
}
#endif

#endif /* VECTOR_TABLE_TYPES_H */

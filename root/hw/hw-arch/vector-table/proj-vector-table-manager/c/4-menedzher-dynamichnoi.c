#include "vector_table_types.h"

extern vtm_status_t mpu_init_vector_protection(uintptr_t base_address, size_t size_bytes);
extern void mpu_grant_write_access(void);
extern void mpu_restore_read_only_access(void);
extern void cache_flush_and_invalidate_range(uintptr_t start_addr, size_t length);

#define SCB_VTOR_REG         (*(volatile uint32_t*)0xE000ED08UL)

/* Статичний вирівняний буфер у пам'яті SRAM */
static isr_vector_t sram_vectors[VECTOR_TABLE_TOTAL_SLOTS] __attribute__((aligned(VECTOR_TABLE_ALIGNMENT_BYTES)));

/* Резервна копія початкових векторів із Flash для відкату */
static isr_vector_t flash_backup_vectors[VECTOR_TABLE_TOTAL_SLOTS];

static bool is_manager_active = false;

vtm_status_t vtm_initialize(void) {
    if (is_manager_active) {
        return VTM_STATUS_ERROR_ALREADY_INITIALIZED;
    }

    uintptr_t sram_base = (uintptr_t)sram_vectors;
    if ((sram_base % VECTOR_TABLE_ALIGNMENT_BYTES) != 0) {
        return VTM_STATUS_ERROR_ALIGNMENT;
    }

    /* 1. Зчитування поточної адреси з VTOR */
    uintptr_t initial_vtor = (uintptr_t)SCB_VTOR_REG;
    const isr_vector_t *src_table = (const isr_vector_t*)initial_vtor;

    /* 2. Копіювання початкових векторів */
    for (size_t i = 0; i < VECTOR_TABLE_TOTAL_SLOTS; ++i) {
        sram_vectors[i] = src_table[i];
        flash_backup_vectors[i] = src_table[i];
    }

    /* 3. Синхронізація кешу перед перемиканням */
    cache_flush_and_invalidate_range(sram_base, sizeof(sram_vectors));

    /* 4. Атомарне перемикання VTOR */
    __asm__ volatile ("cpsid i" : : : "memory");
    SCB_VTOR_REG = (uint32_t)sram_base;
    __asm__ volatile ("dsb 0xF" : : : "memory");
    __asm__ volatile ("isb 0xF" : : : "memory");
    __asm__ volatile ("cpsie i" : : : "memory");

    /* 5. Активація захисту MPU */
    vtm_status_t mpu_status = mpu_init_vector_protection(sram_base, sizeof(sram_vectors));
    if (mpu_status != VTM_STATUS_OK) {
        return mpu_status;
    }

    is_manager_active = true;
    return VTM_STATUS_OK;
}

vtm_status_t vtm_register_handler(int16_t irq_num, isr_vector_t new_handler, isr_vector_t *previous_handler) {
    if (!is_manager_active) {
        vtm_status_t init_res = vtm_initialize();
        if (init_res != VTM_STATUS_OK) {
            return init_res;
        }
    }

    if (new_handler == NULL) {
        return VTM_STATUS_ERROR_NULL_PTR;
    }

    /* Перевірка діапазону (від NMI (-14) до MAX_IRQ) */
    if (irq_num < -14 || irq_num >= (int16_t)CORTEX_M_MAX_IRQ_COUNT) {
        return VTM_STATUS_ERROR_INVALID_IRQ_NUM;
    }

    /* Перевірка обов'язкового біта Thumb */
    uintptr_t fn_addr = (uintptr_t)new_handler;
    if ((fn_addr & 1UL) == 0) {
        return VTM_STATUS_ERROR_INVALID_THUMB_BIT;
    }

    size_t slot_idx = (size_t)(irq_num + (int16_t)CORTEX_M_SYS_EXCEPTIONS_COUNT);

    if (previous_handler != NULL) {
        *previous_handler = sram_vectors[slot_idx];
    }

    /* Атомарна підміна слота з відкриттям MPU */
    __asm__ volatile ("cpsid i" : : : "memory");
    mpu_grant_write_access();

    sram_vectors[slot_idx] = new_handler;

    mpu_restore_read_only_access();
    __asm__ volatile ("cpsie i" : : : "memory");

    /* Синхронізація зміненого 32-бітного слова */
    cache_flush_and_invalidate_range((uintptr_t)&sram_vectors[slot_idx], sizeof(isr_vector_t));

    return VTM_STATUS_OK;
}

vtm_status_t vtm_unregister_handler(int16_t irq_num) {
    if (!is_manager_active) {
        return VTM_STATUS_ERROR_NOT_INITIALIZED;
    }

    if (irq_num < -14 || irq_num >= (int16_t)CORTEX_M_MAX_IRQ_COUNT) {
        return VTM_STATUS_ERROR_INVALID_IRQ_NUM;
    }

    size_t slot_idx = (size_t)(irq_num + (int16_t)CORTEX_M_SYS_EXCEPTIONS_COUNT);
    isr_vector_t default_handler = flash_backup_vectors[slot_idx];

    __asm__ volatile ("cpsid i" : : : "memory");
    mpu_grant_write_access();

    sram_vectors[slot_idx] = default_handler;

    mpu_restore_read_only_access();
    __asm__ volatile ("cpsie i" : : : "memory");

    cache_flush_and_invalidate_range((uintptr_t)&sram_vectors[slot_idx], sizeof(isr_vector_t));

    return VTM_STATUS_OK;
}

bool vtm_is_active(void) {
    return is_manager_active;
}

uintptr_t vtm_get_sram_table_address(void) {
    return (uintptr_t)sram_vectors;
}

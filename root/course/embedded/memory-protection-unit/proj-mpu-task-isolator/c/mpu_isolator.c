#include "mpu_isolator.h"
#include <string.h>

/* Бар'єри синхронізації пам'яті для архітектур ARM Cortex-M */
#if defined(__GNUC__) || defined(__clang__)
    #define __MPU_DMB() __asm volatile("dmb 0xF" ::: "memory")
    #define __MPU_DSB() __asm volatile("dsb 0xF" ::: "memory")
    #define __MPU_ISB() __asm volatile("isb 0xF" ::: "memory")
#else
    #define __MPU_DMB()
    #define __MPU_DSB()
    #define __MPU_ISB()
#endif

/* Поточний стан ізолятора */
static struct {
    mpu_arch_t           arch;
    uint32_t             total_regions;
    bool                 initialized;
    mpu_fault_callback_t fault_callback;
    const mpu_task_isolation_desc_t *current_task;
} g_mpu_state = {0};

/* Допоміжна функція обчислення поля SIZE для PMSAv7: 2^(SIZE+1) */
static uint32_t pmsav7_encode_size(uint32_t size_bytes) {
    if (size_bytes < 32U) {
        return 0U;
    }
    uint32_t size_field = 0U;
    uint32_t temp = size_bytes;
    while ((temp & 1U) == 0U) {
        temp >>= 1U;
        size_field++;
    }
    /* Якщо розмір не є точним ступенем двійки, повертаємо 0 (помилка) */
    if (temp != 1U) {
        return 0U;
    }
    return (size_field - 1U);
}

/* Ініціалізація MPU та винятку MemManage */
int32_t mpu_isolator_init(mpu_arch_t arch, bool use_priv_default) {
    /* Перевірка наявності MPU в кремнії */
    uint32_t type = MPU_TYPE_REG;
    uint32_t dregion = (type >> 8) & 0xFFU;
    if (dregion == 0U) {
        return -1; /* MPU апаратно відсутній на цьому ядрі */
    }

    g_mpu_state.arch = arch;
    g_mpu_state.total_regions = dregion;
    g_mpu_state.initialized = false;
    g_mpu_state.fault_callback = NULL;
    g_mpu_state.current_task = NULL;

    /* Вимикаємо MPU перед конфігурацією з бар'єрами */
    __MPU_DMB();
    MPU_CTRL_REG = 0U;
    __MPU_DSB();
    __MPU_ISB();

    /* Якщо PMSAv8, ініціалізуємо таблицю атрибутів пам'яті MAIR */
    if (arch == MPU_ARCH_PMSAV8) {
        /*
         * Attr 0: Device-nGnRnE (0x00) - Периферія
         * Attr 1: Normal Non-cacheable (0x44) - DMA буфери
         * Attr 2: Normal Write-Through (0xBB) - Flash / RAM WT
         * Attr 3: Normal Write-Back Read/Write-Allocate (0xFF) - RAM швидка
         */
        MPU_MAIR0_REG = 0xBB4400FFUL; /* Attr3=0xBB, Attr2=0x44, Attr1=0x00, Attr0=0xFF */
        MPU_MAIR1_REG = 0x00000000UL;
    }

    /* Активація системного обробника MemManage у SCB */
    SCB_SHCSR_REG |= SCB_SHCSR_MEMFAULTENA_MSK;

    /* Формуємо біти MPU_CTRL */
    uint32_t ctrl = MPU_CTRL_ENABLE_MSK;
    if (use_priv_default) {
        ctrl |= MPU_CTRL_PRIVDEFENA_MSK;
    }
    /* Дозволяємо роботу MPU під час HardFault та NMI для максимального захисту */
    ctrl |= MPU_CTRL_HFNMIENA_MSK;

    MPU_CTRL_REG = ctrl;
    __MPU_DSB();
    __MPU_ISB();

    g_mpu_state.initialized = true;
    return 0;
}

/* Конфігурація конкретного регіону */
int32_t mpu_configure_region(const mpu_region_config_t *config) {
    if (!config || config->region_number >= g_mpu_state.total_regions) {
        return -1;
    }

    /* Обираємо слот регіону через RNR */
    MPU_RNR_REG = config->region_number;

    if (g_mpu_state.arch == MPU_ARCH_PMSAV7) {
        /* PMSAv7: перевірка вирівнювання бази на розмір */
        uint32_t size_field = pmsav7_encode_size(config->size_bytes);
        if (size_field == 0U && config->size_bytes != 0U) {
            return -2; /* Некоректний розмір (не 2^N або < 32B) */
        }
        if ((config->base_address & (config->size_bytes - 1U)) != 0U) {
            return -3; /* Базова адреса не вирівняна на розмір */
        }

        /* Запис RBAR: базова адреса */
        MPU_RBAR_REG = (config->base_address & 0xFFFFFFE0UL);

        /* Формування RASR */
        uint32_t rasr = 0U;
        if (config->size_bytes > 0U) {
            rasr |= 1UL; /* Біт ENABLE */
            rasr |= (size_field << 1);
            rasr |= (((uint32_t)config->subregion_disable & 0xFFU) << 8);

            /* Кодування атрибутів пам'яті (TEX, C, B, S) */
            uint32_t tex = 0U, c = 0U, b = 0U, s = 1U;
            switch (config->memory_attr) {
                case MPU_ATTR_DEVICE_nGnRnE:
                    tex = 0; c = 0; b = 0; s = 1;
                    break;
                case MPU_ATTR_DEVICE_nGnRE:
                    tex = 0; c = 0; b = 1; s = 1;
                    break;
                case MPU_ATTR_NORMAL_NONCACHE:
                    tex = 1; c = 0; b = 0; s = 1;
                    break;
                case MPU_ATTR_NORMAL_WT:
                    tex = 0; c = 1; b = 0; s = 0;
                    break;
                case MPU_ATTR_NORMAL_WB_WA:
                default:
                    tex = 1; c = 1; b = 1; s = 1;
                    break;
            }

            rasr |= (b << 16);
            rasr |= (c << 17);
            rasr |= (s << 18);
            rasr |= (tex << 19);
            rasr |= (((uint32_t)config->access_perm & 0x07U) << 24);
            if (config->execute_never) {
                rasr |= (1UL << 28); /* XN біт */
            }
        }
        MPU_RASR_REG = rasr;

    } else {
        /* PMSAv8: Base та Limit з 32-байтним вирівнюванням */
        if ((config->base_address & 0x1FUL) != 0U) {
            return -4; /* Базова адреса не вирівняна на 32 байти */
        }
        uint32_t limit_address = config->base_address + config->size_bytes - 1U;
        if (config->size_bytes == 0U) {
            limit_address = config->base_address;
        }

        /* Запис RBAR: [31:5] Base, [4:3] SH, [2:1] AP, [0] XN */
        uint32_t rbar = (config->base_address & 0xFFFFFFE0UL);
        rbar |= (0x02UL << 3); /* Outer Shareable */
        rbar |= (((uint32_t)config->access_perm & 0x03U) << 1);
        if (config->execute_never) {
            rbar |= 1UL; /* XN біт у PMSAv8 знаходиться в біті 0 RBAR */
        }
        MPU_RBAR_REG = rbar;

        /* Запис RLAR: [31:5] Limit, [3:1] AttrIndx, [0] Enable */
        uint32_t rlar = (limit_address & 0xFFFFFFE0UL);
        uint32_t attr_idx = 0U;
        switch (config->memory_attr) {
            case MPU_ATTR_DEVICE_nGnRnE:   attr_idx = 1U; break;
            case MPU_ATTR_NORMAL_NONCACHE: attr_idx = 2U; break;
            case MPU_ATTR_NORMAL_WT:       attr_idx = 3U; break;
            case MPU_ATTR_NORMAL_WB_WA:
            default:                       attr_idx = 0U; break;
        }
        rlar |= (attr_idx << 1);
        if (config->size_bytes > 0U) {
            rlar |= 1UL; /* Enable біт */
        }
        MPU_RLAR_REG = rlar;
    }

    __MPU_DSB();
    __MPU_ISB();
    return 0;
}

/* Вимкнення конкретного регіону */
int32_t mpu_disable_region(uint8_t region_number) {
    if (region_number >= g_mpu_state.total_regions) {
        return -1;
    }
    MPU_RNR_REG = region_number;
    if (g_mpu_state.arch == MPU_ARCH_PMSAV7) {
        MPU_RASR_REG = 0U;
    } else {
        MPU_RLAR_REG = 0U;
    }
    __MPU_DSB();
    __MPU_ISB();
    return 0;
}

/* Швидке перемикання контексту задач RTOS у PendSV */
void mpu_switch_task_context(const mpu_task_isolation_desc_t *task_desc) {
    if (!task_desc) {
        return;
    }

    g_mpu_state.current_task = task_desc;

    if (g_mpu_state.arch == MPU_ARCH_PMSAV7) {
        /*
         * PMSAv7 оптимізований запис з бітом VALID (біт 4 в RBAR).
         * Це дозволяє записати номер регіону та базову адресу за одну інструкцію!
         */

        /* 1. Регіон 5: Стек задачі (Unprivileged RW, XN) */
        uint32_t stack_size_field = pmsav7_encode_size(task_desc->stack_size);
        MPU_RBAR_REG = (task_desc->stack_base & 0xFFFFFFE0UL) | (1UL << 4) | MPU_TASK_STACK_REGION;
        MPU_RASR_REG = 1UL | (stack_size_field << 1) | ((uint32_t)MPU_AP_PRIV_RW_UNPRIV_RW << 24) | (1UL << 28) | (1UL << 18) | (1UL << 19) | (1UL << 17) | (1UL << 16);

        /* 2. Регіон 6: Захисна смуга переповнення стека (No Access, XN) */
        uint32_t guard_size_field = pmsav7_encode_size(task_desc->guard_size);
        MPU_RBAR_REG = (task_desc->stack_base & 0xFFFFFFE0UL) | (1UL << 4) | MPU_TASK_GUARD_REGION;
        MPU_RASR_REG = 1UL | (guard_size_field << 1) | ((uint32_t)MPU_AP_NO_ACCESS << 24) | (1UL << 28);

        /* 3. Регіон 7: Приватні дані задачі (Unprivileged RW, XN) */
        if (task_desc->private_data_size > 0U) {
            uint32_t priv_size_field = pmsav7_encode_size(task_desc->private_data_size);
            MPU_RBAR_REG = (task_desc->private_data_base & 0xFFFFFFE0UL) | (1UL << 4) | MPU_TASK_PRIVATE_REGION;
            MPU_RASR_REG = 1UL | (priv_size_field << 1) | ((uint32_t)MPU_AP_PRIV_RW_UNPRIV_RW << 24) | (1UL << 28) | (1UL << 18) | (1UL << 19) | (1UL << 17) | (1UL << 16);
        } else {
            MPU_RBAR_REG = (1UL << 4) | MPU_TASK_PRIVATE_REGION;
            MPU_RASR_REG = 0U; /* Вимкнено */
        }

    } else {
        /* PMSAv8: Запис через RNR, RBAR, RLAR */

        /* 1. Регіон 5: Стек задачі */
        MPU_RNR_REG = MPU_TASK_STACK_REGION;
        MPU_RBAR_REG = (task_desc->stack_base & 0xFFFFFFE0UL) | ((uint32_t)MPU_AP_PRIV_RW_UNPRIV_RW << 1) | 1UL;
        MPU_RLAR_REG = ((task_desc->stack_base + task_desc->stack_size - 1U) & 0xFFFFFFE0UL) | (0U << 1) | 1UL;

        /* 2. Регіон 6: Захисна смуга стека (No Access) */
        MPU_RNR_REG = MPU_TASK_GUARD_REGION;
        MPU_RBAR_REG = (task_desc->stack_base & 0xFFFFFFE0UL) | ((uint32_t)MPU_AP_NO_ACCESS << 1) | 1UL;
        MPU_RLAR_REG = ((task_desc->stack_base + task_desc->guard_size - 1U) & 0xFFFFFFE0UL) | (0U << 1) | 1UL;

        /* 3. Регіон 7: Приватні дані задачі */
        MPU_RNR_REG = MPU_TASK_PRIVATE_REGION;
        if (task_desc->private_data_size > 0U) {
            MPU_RBAR_REG = (task_desc->private_data_base & 0xFFFFFFE0UL) | ((uint32_t)MPU_AP_PRIV_RW_UNPRIV_RW << 1) | 1UL;
            MPU_RLAR_REG = ((task_desc->private_data_base + task_desc->private_data_size - 1U) & 0xFFFFFFE0UL) | (0U << 1) | 1UL;
        } else {
            MPU_RLAR_REG = 0U;
        }
    }

    /* Критично важливі бар'єри синхронізації */
    __MPU_DSB();
    __MPU_ISB();
}

/* Перевірка буфера для захисту від Confused Deputy атак у системних викликах */
bool mpu_validate_buffer(const void *buffer, size_t length, bool write_access) {
    (void)write_access;
    if (!buffer || length == 0U) {
        return false;
    }

    uintptr_t start = (uintptr_t)buffer;
    uintptr_t end   = start + length;
    if (end < start) {
        return false; /* Переповнення адресного простору (integer wrap-around) */
    }

    const mpu_task_isolation_desc_t *task = g_mpu_state.current_task;
    if (!task) {
        /* Якщо викликано поза контекстом задачі (з ядра), дозволяємо */
        return true;
    }

    /* Перевіряємо, чи потрапляє буфер у стек задачі (вище захисної смуги) */
    uintptr_t stack_usable_start = task->stack_base + task->guard_size;
    uintptr_t stack_end          = task->stack_base + task->stack_size;
    if (start >= stack_usable_start && end <= stack_end) {
        return true;
    }

    /* Перевіряємо, чи потрапляє буфер у приватну пам'ять задачі */
    if (task->private_data_size > 0U) {
        uintptr_t priv_start = task->private_data_base;
        uintptr_t priv_end   = task->private_data_base + task->private_data_size;
        if (start >= priv_start && end <= priv_end) {
            return true;
        }
    }

    /* Буфер виходить за межі дозволеної пам'яті поточної задачі */
    return false;
}

/* Реєстрація користувацького обробника збоїв */
void mpu_register_fault_callback(mpu_fault_callback_t callback) {
    g_mpu_state.fault_callback = callback;
}

/* Обробка MemManage винятку на рівні мови C */
void mpu_memmanage_c_handler(mpu_fault_stack_frame_t *stack_frame, uint32_t exc_return) {
    uint32_t cfsr  = SCB_CFSR_REG;
    uint8_t  mmfsr = (uint8_t)(cfsr & 0xFFU);
    uint32_t mmfar = SCB_MMFAR_REG;

    mpu_fault_report_t report;
    memset(&report, 0, sizeof(report));

    report.fault_status_flags = mmfsr;
    report.is_address_valid   = ((mmfsr & MMFSR_MMARVALID_MSK) != 0U);
    report.fault_address      = report.is_address_valid ? mmfar : 0x00000000UL;
    report.occurred_in_psp    = ((exc_return & (1UL << 2)) != 0U);

    if (stack_frame) {
        report.fault_pc  = stack_frame->pc;
        report.fault_lr  = stack_frame->lr;
        report.fault_psr = stack_frame->xpsr;
    }

    /* Виклик зареєстрованого колбеку користувача */
    if (g_mpu_state.fault_callback) {
        g_mpu_state.fault_callback(&report);
    }

    /* Очищення бітів MemManage у SCB->CFSR шляхом запису 1 */
    SCB_CFSR_REG = (cfsr & 0xFFUL);
    __MPU_DSB();
    __MPU_ISB();
}

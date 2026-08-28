typedef enum {
    FAULT_INJECT_NONE = 0,
    FAULT_INJECT_STACK_CORRUPT,
    FAULT_INJECT_UNDERVOLTAGE,
    FAULT_INJECT_CAN_BUSOFF,
    FAULT_INJECT_I2C_LOCKUP
} health_fault_inject_mode_t;

typedef struct {
    health_fault_inject_mode_t active_mode;
    uint32_t                   duration_ticks;
} health_fault_injector_t;

void health_fault_injector_init(health_fault_injector_t *inj) {
    if (!inj) return;
    inj->active_mode = FAULT_INJECT_NONE;
    inj->duration_ticks = 0;
}

void health_fault_inject_trigger(health_fault_injector_t *inj, 
                                 health_fault_inject_mode_t mode, 
                                 uint32_t duration_ticks) {
    if (!inj) return;
    inj->active_mode = mode;
    inj->duration_ticks = duration_ticks;
}

uint16_t health_fault_inject_apply(health_fault_injector_t *inj, 
                                   health_fault_inject_mode_t target_mode, 
                                   uint16_t actual_value) {
    if (!inj || inj->active_mode != target_mode || inj->duration_ticks == 0) {
        return actual_value;
    }

    inj->duration_ticks--;
    if (inj->duration_ticks == 0) {
        inj->active_mode = FAULT_INJECT_NONE;
    }

    // Повернення деградованого значення залежно від типу інжекції
    switch (target_mode) {
        case FAULT_INJECT_UNDERVOLTAGE: return 100; // Просідання живлення
        case FAULT_INJECT_CAN_BUSOFF:   return 0;   // Bus-Off
        case FAULT_INJECT_I2C_LOCKUP:   return 50;  // Зависання шини
        case FAULT_INJECT_STACK_CORRUPT: return 0;  // Пошкодження стека
        default: return actual_value;
    }
}

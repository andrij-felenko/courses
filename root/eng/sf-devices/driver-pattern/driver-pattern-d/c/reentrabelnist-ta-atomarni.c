/* Безпечна критична секція зі збереженням попереднього стану переривань */
typedef uint32_t critical_section_t;

static inline critical_section_t enter_critical_section(void) {
    critical_section_t primask = __get_PRIMASK();
    __disable_irq();
    return primask;
}

static inline void exit_critical_section(critical_section_t primask) {
    __set_PRIMASK(primask);
}

driver_status_t i2c_try_lock_state(i2c_handle_t* handle) {
    critical_section_t cs = enter_critical_section();
    if (handle->state != I2C_STATE_IDLE) {
        exit_critical_section(cs);
        return DRIVER_STATUS_BUSY;
    }
    handle->state = I2C_STATE_BUSY_TX;
    exit_critical_section(cs);
    return DRIVER_STATUS_OK;
}

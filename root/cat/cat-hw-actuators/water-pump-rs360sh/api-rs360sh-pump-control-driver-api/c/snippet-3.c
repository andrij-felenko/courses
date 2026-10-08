typedef enum {
    RS360_STATE_STOPPED = 0,
    RS360_STATE_SOFT_START,
    RS360_STATE_RUNNING,
    RS360_STATE_ERROR_DRY_RUN,
    RS360_STATE_ERROR_OVERCURRENT,
    RS360_STATE_EMERGENCY_STOP
} rs360_state_t;

// Обробка діагностики (викликається регулярним циклом контролю)
rs360_error_t rs360_process_diagnostics(rs360_handle_t dev);

// Отримання поточного стану та виміряних параметрів
rs360_error_t rs360_get_status(rs360_handle_t dev, rs360_state_t *state, float *current_amps);

// Негайна екстрена зупинка помпи (апаратна або програмна)
void rs360_emergency_stop(rs360_handle_t dev);

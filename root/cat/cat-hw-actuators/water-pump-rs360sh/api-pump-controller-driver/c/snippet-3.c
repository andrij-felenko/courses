// Статусна структура та діагностичний інтерфейс на C
typedef enum {
    PUMP_STATE_READY = 0,
    PUMP_STATE_PUMPING,
    PUMP_STATE_FAULT_TIMEOUT,
    PUMP_STATE_FAULT_EMERGENCY
} pump_state_t;

typedef struct {
    pump_state_t state;           // Поточний стан автомата
    float        dispensed_ml;    // Уже вилитий об'єм поточної сесії
    uint32_t     remaining_ms;    // Час до завершення дозування
} pump_status_t;

pump_status_t pump_get_status(void);
pump_err_t    pump_reset_fault(void);

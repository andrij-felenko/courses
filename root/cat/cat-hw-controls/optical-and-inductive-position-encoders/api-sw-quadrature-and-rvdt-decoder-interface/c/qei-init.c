typedef struct {
    uint32_t sample_rate_hz;
    uint8_t filter_depth;
    bool enable_z_index;
} qei_config_t;

typedef struct {
    void* instance;
    volatile int32_t position;
    uint32_t errors;
} qei_driver_t;

int qei_init(qei_driver_t* drv, const qei_config_t* cfg) {
    if (!drv || !cfg) return -1;
    drv->position = 0;
    drv->errors = 0;
    // Налаштування апаратних регістрів QEI та фільтрації
    return 0;
}

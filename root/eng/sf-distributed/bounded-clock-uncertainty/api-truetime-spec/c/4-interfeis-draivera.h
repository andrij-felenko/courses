/* Інтерфейс плагіна апаратного джерела */
typedef struct {
    const char *driver_name;
    
    /* Ініціалізація апаратного пристрою (відкриття дескрипторів /dev/ptpX або /dev/ppsX) */
    int (*init)(void);
    
    /* Отримання поточного зсуву та похибки від зовнішнього еталону */
    int (*poll_sample)(int64_t *utc_time_ns, int64_t *reference_error_ns);
    
    /* Плавне коригування частоти локального генератора (ppb, parts-per-billion) */
    int (*adjust_frequency_ppb)(double offset_ppb);
    
    /* Звільнення ресурсів при зупинці демона */
    void (*shutdown)(void);
} tt_hardware_driver_t;

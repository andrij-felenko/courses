/* Типовий Platform Abstraction Layer сучасного вендорського C-драйвера */
typedef int8_t (*sensor_read_fptr_t)(uint8_t reg_addr, uint8_t *read_data, uint32_t len, void *intf_ptr);
typedef int8_t (*sensor_write_fptr_t)(uint8_t reg_addr, const uint8_t *write_data, uint32_t len, void *intf_ptr);
typedef void (*sensor_delay_us_fptr_t)(uint32_t period_us, void *intf_ptr);

struct sensor_dev {
    uint8_t chip_id;            /* Зчитаний ідентифікатор мікросхеми */
    void *intf_ptr;             /* Непрозорий вказівник користувача на контекст шини або об'єкт */
    sensor_read_fptr_t read;    /* Вказівник на системну функцію читання з шини */
    sensor_write_fptr_t write;  /* Вказівник на системну функцію запису в шину */
    sensor_delay_us_fptr_t delay_us; /* Вказівник на системну затримку в мікросекундах */
    
    /* Внутрішній стан чипа: калібрувальні коефіцієнти */
    struct {
        uint16_t dig_t1;
        int16_t  dig_t2;
        int16_t  dig_t3;
    } calib_data;
};

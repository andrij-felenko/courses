// Коди помилок драйвера
typedef enum {
    ENCODER_OK = 0,
    ENCODER_ERR_TIMEOUT,
    ENCODER_ERR_CRC,
    ENCODER_ERR_HARDWARE_FAULT,
    ENCODER_ERR_LOW_BATTERY
} encoder_status_t;

// Обробка статусного кадру
encoder_status_t encoder_process_frame(uint64_t raw_frame, const encoder_config_t* cfg, encoder_data_t* data) {
    bool err_bit = (raw_frame >> 1) & 1;
    bool warn_bit = raw_frame & 1;

    if (!err_bit) {
        data->error_flag = true;
        return ENCODER_ERR_HARDWARE_FAULT;
    }
    data->warning_flag = !warn_bit;
    
    // Перевірка CRC та розпакування бітів
    return ENCODER_OK;
}

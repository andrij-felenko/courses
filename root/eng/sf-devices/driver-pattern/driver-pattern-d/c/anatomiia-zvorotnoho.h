/* Зворотний виклик із повним контекстом */
typedef void (*i2c_callback_t)(i2c_handle_t* handle,
                               driver_status_t status,
                               size_t bytes_transferred,
                               void* user_data);

/* Реєстрація або передача в асинхронний виклик */
driver_status_t i2c_master_transfer_async(i2c_handle_t* handle,
                                          uint8_t dev_addr,
                                          const uint8_t* tx_data, size_t tx_len,
                                          uint8_t* rx_data, size_t rx_len,
                                          i2c_callback_t callback,
                                          void* user_data);

/* Структура дескриптора транзакції на C99 */
typedef struct i2c_transaction_s {
    uint8_t dev_addr;
    const uint8_t* tx_data;
    size_t tx_len;
    uint8_t* rx_data;
    size_t rx_len;
    i2c_callback_t callback;
    void* user_data;
    bool hold_bus; /* Прапорець Repeated Start */
} i2c_transaction_t;

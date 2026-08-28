typedef void (*bus_async_cb_t)(bus_status_t status, void *user_arg);

typedef struct {
    uint16_t        reg_addr;
    uint8_t        *rx_buffer;
    const uint8_t  *tx_buffer;
    size_t          length;
    bus_async_cb_t  callback;
    void           *user_arg;
} bus_async_request_t;

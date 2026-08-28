typedef void (*bus_callback_fn)(bus_status_t status, void *user_arg);

typedef struct {
    uint16_t         reg_addr;
    uint8_t         *rx_buf;
    const uint8_t   *tx_buf;
    size_t           len;
    bus_callback_fn  callback;
    void            *user_arg;
} bus_async_request_t;

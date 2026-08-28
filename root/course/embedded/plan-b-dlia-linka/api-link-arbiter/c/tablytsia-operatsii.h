struct bearer_interface;

typedef struct {
    int  (*init)(struct bearer_interface *self);
    int  (*send)(struct bearer_interface *self, const uint8_t *data, size_t len, qos_priority_t prio);
    int  (*poll_rx)(struct bearer_interface *self, uint8_t *buf, size_t max_len, bearer_metrics_t *out_metrics);
    void (*get_metrics)(struct bearer_interface *self, bearer_metrics_t *out_metrics);
    void (*set_active)(struct bearer_interface *self, bool active);
    int  (*set_frequency_band)(struct bearer_interface *self, uint32_t freq_hz);
} bearer_ops_t;

typedef struct bearer_interface {
    bearer_id_t          id;
    const char          *name;
    const bearer_ops_t  *ops;
    void                *driver_priv;   /* Вказівник на апаратно-залежний контекст драйвера */
    bearer_metrics_t     metrics;
    uint32_t             tx_byte_count;
    uint32_t             rx_byte_count;
    uint32_t             tx_drop_count;
} bearer_interface_t;

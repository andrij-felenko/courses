typedef struct {
    uint8_t  failover_per_thresh;   /* Поріг втрат для переходу на резерв (типово 25%) */
    int16_t  failover_rssi_thresh;  /* Поріг RSSI для переходу на резерв (типово -95 дБм) */
    uint8_t  loss_burst_limit;      /* Ліміт поспіль втрачених пакетів до аварійного скидання */
    
    uint8_t  recovery_per_thresh;   /* Поріг втрат для повернення на основний (типово 5%) */
    uint16_t recovery_dwell_ms;     /* Час стабільності перед поверненням (типово 4000-6000 мс) */
    uint16_t recovery_packet_streak;/* Кількість поспіль успішних пакетів для відновлення */
    
    uint16_t heartbeat_timeout_ms;  /* Таймаут повної тиші перед переходом в автономію (3000 мс) */
    bool     enable_rf_switch_gpio; /* Керувати апаратним RF Switch (SPDT) через GPIO */
    uint8_t  rf_switch_gpio_pin;    /* Номер GPIO для апаратного ключа */
} arbiter_config_t;

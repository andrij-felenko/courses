typedef enum {
    BITBANG_OK              = 0,  // Успішне завершення операції
    BITBANG_ERR_TIMEOUT     = 1,  // Перевищено ліміт очікування лінії
    BITBANG_ERR_BUS_BUSY    = 2,  // Лінія заблокована у невідповідному стані
    BITBANG_ERR_COLLISION   = 3,  // Виявлено конфлікт рівнів на шині
    BITBANG_ERR_INVALID_ARG = 4   // Передано некоректні параметри або нульовий вказівник
} bitbang_status_t;

typedef struct {
    volatile uint32_t *port_bsrr;     // Адреса регістра BSRR порту
    volatile uint32_t *port_idr;      // Адреса регістра IDR порту
    uint16_t           pin_sclk;      // Номер виводу тактування (0..15)
    uint16_t           pin_data;      // Номер виводу даних (0..15)
    uint32_t           delay_setup;   // Затримка t_setup у тактах ядра
    uint32_t           delay_hold;    // Затримка t_hold у тактах ядра
    uint32_t           delay_half_clk;// Тривалість півперіоду такту в тактах
} bitbang_config_t;

bitbang_status_t bitbang_init(const bitbang_config_t *config);
bitbang_status_t bitbang_transfer_byte(const bitbang_config_t *config, uint8_t tx_byte, uint8_t *rx_byte);

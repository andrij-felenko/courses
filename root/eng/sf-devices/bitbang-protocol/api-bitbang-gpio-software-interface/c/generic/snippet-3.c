typedef struct {
    void* data_port;       // Порт лінії даних
    uint16_t data_pin;     // Номер виводу даних
    void* clock_port;      // Порт лінії тактування
    uint16_t clock_pin;    // Номер виводу тактування
    uint32_t delay_us;     // Затримка на півперіоду тактового сигналу
} bitbang_config_t;

// Ініціалізація шини
int bitbang_init(bitbang_config_t* config);

// Запис одного байта
int bitbang_write_byte(bitbang_config_t* config, uint8_t byte);

// Читання масиву байтів
int bitbang_read_buffer(bitbang_config_t* config, uint8_t* buffer, size_t length);

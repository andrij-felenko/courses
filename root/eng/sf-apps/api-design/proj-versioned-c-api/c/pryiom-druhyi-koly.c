// sensor.h  —  versioned config: size ПЕРШИМ полем
typedef struct {
    size_t   size;          // ← скільки байтів у ЦІЙ структурі; заповнює клієнт
    int      pin;
    uint32_t rate_hz;
} sensor_config_t;

// зручний ініціалізатор, що проставляє size автоматично
#define SENSOR_CONFIG_INIT  { .size = sizeof(sensor_config_t) }

sensor_t *sensor_open(const sensor_config_t *cfg);

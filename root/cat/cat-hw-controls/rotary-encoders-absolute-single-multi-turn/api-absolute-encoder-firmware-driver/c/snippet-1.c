#include <stdint.h>
#include <stdbool.h>

// Тип протоколу енкодера
typedef enum {
    ENCODER_PROTO_SSI = 0,
    ENCODER_PROTO_BISS_C = 1
} encoder_proto_t;

// Конфігурація апаратного інтерфейсу та параметрів кадру
typedef struct {
    encoder_proto_t protocol;
    uint8_t singleturn_bits;  // Наприклад, 14 біт
    uint8_t multiturn_bits;   // Наприклад, 12 біт (0 для single-turn)
    bool use_gray_code;       // true, якщо диск видає код Ґрея
    uint32_t timeout_us;      // Тайм-аут зчитування в мікросекундах
} encoder_config_t;

// Структура вихідних декодованих даних та діагностики
typedef struct {
    uint32_t raw_singleturn;
    uint32_t raw_multiturn;
    uint64_t full_position;
    bool error_flag;
    bool warning_flag;
    uint8_t crc_error_count;
} encoder_data_t;

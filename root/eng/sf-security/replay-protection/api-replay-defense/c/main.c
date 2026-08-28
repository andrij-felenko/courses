#include <stdint.h>

// Базовий заголовок ESP (RFC 4303)
struct esp_header {
    uint32_t spi;       // Ідентифікатор Security Association (SA)
    uint32_t seq_no;    // Молодші 32 біти лічильника послідовності (Sequence Number)
};

// Трейлер ESP
struct esp_trailer {
    uint8_t pad_length; // Кількість байтів вирівнювання (0..255)
    uint8_t next_proto; // Тип вкладеного протоколу (IPv4=4, IPv6=41, TCP=6, UDP=17)
};

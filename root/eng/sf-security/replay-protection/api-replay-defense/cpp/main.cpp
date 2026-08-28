#include <cstdint>
#include <cstddef>

// Базовий заголовок ESP (RFC 4303)
struct EspHeader {
    uint32_t spi{0};       // Ідентифікатор Security Association (SA)
    uint32_t seq_no{0};    // Молодші 32 біти лічильника послідовності (Sequence Number)
};

// Трейлер ESP
struct EspTrailer {
    uint8_t pad_length{0}; // Кількість байтів вирівнювання (0..255)
    uint8_t next_proto{0}; // Тип вкладеного протоколу (IPv4=4, IPv6=41, TCP=6, UDP=17)
};

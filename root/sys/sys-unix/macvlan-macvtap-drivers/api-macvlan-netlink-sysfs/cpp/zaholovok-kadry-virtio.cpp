// Ідіоматичне C++20 представлення VirtioNetHdr
#include <cstdint>

struct VirtioNetHdr {
    std::uint8_t  flags{0};        // Прапорці апаратного розвантаження
    std::uint8_t  gso_type{0};     // Тип сегментації (TSO4, TSO6, UDP GSO)
    std::uint16_t hdr_len{0};      // Загальна довжина заголовків L2/L3/L4
    std::uint16_t gso_size{0};     // Максимальний розмір сегмента MSS
    std::uint16_t csum_start{0};   // Зміщення для обчислення CRC
    std::uint16_t csum_offset{0};  // Зміщення поля запису CRC
};

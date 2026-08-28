#pragma pack(push, 1)
struct alignas(1) SwimProbeHeader {
    uint16_t magic{0x5357};  // Магічне число протоколу ("SW")
    uint8_t  msg_type{0};    // Код операції
    uint8_t  flags{0};       // Рівень LHM та службові прапорці
    uint64_t seq_no{0};      // Монотонний ідентифікатор зонду
    uint32_t target_ip{0};   // IPv4 адреса цілі
    uint16_t target_port{0}; // Порт цілі
};
#pragma pack(pop)

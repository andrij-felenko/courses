// Статичний поліморфізм мовою C++20 через концепції (Concepts)
#include <cstdint>
#include <span>

template <typename T>
concept BusDevice = requires(T bus, uint8_t byte) {
    { bus.write_byte(byte) } noexcept -> std::same_as<void>;
    { bus.read_byte() } noexcept -> std::same_as<uint8_t>;
};

struct HardwareSpi {
    static inline void write_byte(uint8_t data) noexcept {
        *reinterpret_cast<volatile uint8_t*>(0x4001300CUL) = data;
    }
    static inline uint8_t read_byte() noexcept {
        return *reinterpret_cast<volatile uint8_t*>(0x4001300CUL);
    }
};

template <BusDevice Bus>
void send_packet_cpp(Bus& bus, std::span<const uint8_t> data) noexcept {
    for (uint8_t byte : data) {
        // Метод write_byte повністю вбудовується безпосередньо в тіло циклу!
        bus.write_byte(byte);
    }
}

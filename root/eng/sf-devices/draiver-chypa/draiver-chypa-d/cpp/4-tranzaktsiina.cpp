#include <cstdint>
#include <span>
#include <concepts>

enum class BusError : uint8_t {
    None = 0,
    Timeout,
    Nack,
    BusLocked
};

template <typename T>
concept BusDevice = requires(T bus, uint8_t addr, uint8_t reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { bus.read(addr, reg, rx) } -> std::same_as<BusError>;
    { bus.write(addr, reg, tx) } -> std::same_as<BusError>;
    { bus.readDma(addr, reg, rx) } -> std::same_as<BusError>;
    { bus.delayMs(uint32_t{}) } -> std::same_as<void>;
    { bus.busRecover() } -> std::same_as<void>;
};

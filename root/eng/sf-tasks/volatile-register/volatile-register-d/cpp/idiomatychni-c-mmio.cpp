#include <cstdint>
#include <type_traits>

namespace mmio {

// Політики доступу до регістрів
struct ReadOnly {};
struct WriteOnly {};
struct ReadWrite : ReadOnly, WriteOnly {};

// Шаблонний клас для роботи з окремим регістром
template <std::uintptr_t Address, typename AccessPolicy = ReadWrite, typename T = std::uint32_t>
class Register {
public:
    static_assert(std::is_integral_v<T>, "Регістр повинен бути цілочисельного типу");

    // Читання доступне тільки якщо політика підтримує ReadOnly
    template <typename P = AccessPolicy, typename = std::enable_if_t<std::is_base_of_v<ReadOnly, P>>>
    [[nodiscard]] static T read() noexcept {
        return *reinterpret_cast<const volatile T*>(Address);
    }

    // Запис доступний тільки якщо політика підтримує WriteOnly
    template <typename P = AccessPolicy, typename = std::enable_if_t<std::is_base_of_v<WriteOnly, P>>>
    static void write(T value) noexcept {
        *reinterpret_cast<volatile T*>(Address) = value;
    }

    // Модифікація бітів доступна тільки для ReadWrite
    template <typename P = AccessPolicy, typename = std::enable_if_t<std::is_same_v<ReadWrite, P>>>
    static void set_bits(T mask) noexcept {
        write(read() | mask);
    }

    template <typename P = AccessPolicy, typename = std::enable_if_t<std::is_same_v<ReadWrite, P>>>
    static void clear_bits(T mask) noexcept {
        write(read() & ~mask);
    }
};

// Оголошення конкретних апаратних регістрів за фіксованими адресами
using UART1_CR1 = Register<0x40013800UL, ReadWrite>;
using UART1_SR  = Register<0x40013808UL, ReadOnly>;
using UART1_DR  = Register<0x40013814UL, ReadWrite>;

} // namespace mmio

void transmit_data(std::uint8_t byte) noexcept {
    constexpr std::uint32_t TXE_FLAG = 1U << 7;
    
    // Помилка компіляції виникне, якщо спробувати викликати UART1_SR::write(0)
    while (!(mmio::UART1_SR::read() & TXE_FLAG)) {
        // Опитування статусу
    }
    
    mmio::UART1_DR::write(byte);
}

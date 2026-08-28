/* cpp_mmio_driver.hpp — Завершена заголовна бібліотека C++20 */
#include <cstdint>
#include <cstddef>
#include <type_traits>
#include <concepts>

namespace mcu {

// 1. Політики доступу до апаратного регістру
enum class Access : uint8_t {
    ReadOnly,
    WriteOnly,
    ReadWrite
};

// 2. RAII-блокування глобальних переривань для атомарних операцій RMW
class [[nodiscard]] InterruptLock {
public:
    InterruptLock() noexcept {
        #if defined(__arm__) || defined(__thumb__)
        asm volatile (
            "mrs %0, primask\n"
            "cpsid i\n"
            : "=r" (primask_)
            :
            : "memory"
        );
        #else
        primask_ = 0;
        #endif
    }

    ~InterruptLock() noexcept {
        #if defined(__arm__) || defined(__thumb__)
        asm volatile (
            "msr primask, %0\n"
            :
            : "r" (primask_)
            : "memory"
        );
        #endif
    }

    InterruptLock(const InterruptLock&) = delete;
    InterruptLock& operator=(const InterruptLock&) = delete;
    InterruptLock(InterruptLock&&) = delete;
    InterruptLock& operator=(InterruptLock&&) = delete;

private:
    uint32_t primask_{0};
};

// 3. Шаблон апаратного MMIO-регістра
template <uintptr_t Address, typename T, Access Acc>
struct Register {
    static_assert(std::is_integral_v<T>, "Тип регістру має бути цілочисельним!");

    // Читання дозволено тільки для ReadOnly та ReadWrite
    [[nodiscard]] static inline T read() noexcept 
        requires (Acc == Access::ReadOnly || Acc == Access::ReadWrite) 
    {
        return *reinterpret_cast<volatile T*>(Address);
    }

    // Запис дозволено тільки для WriteOnly та ReadWrite
    static inline void write(T value) noexcept 
        requires (Acc == Access::WriteOnly || Acc == Access::ReadWrite) 
    {
        *reinterpret_cast<volatile T*>(Address) = value;
    }

    // Атомарна модифікація бітів (Read-Modify-Write із блокуванням переривань)
    static inline void set_bits(T mask) noexcept 
        requires (Acc == Access::ReadWrite) 
    {
        InterruptLock lock;
        *reinterpret_cast<volatile T*>(Address) = *reinterpret_cast<volatile T*>(Address) | mask;
    }

    static inline void clear_bits(T mask) noexcept 
        requires (Acc == Access::ReadWrite) 
    {
        InterruptLock lock;
        *reinterpret_cast<volatile T*>(Address) = *reinterpret_cast<volatile T*>(Address) & ~mask;
    }

    static inline void modify(T clear_mask, T set_mask) noexcept
        requires (Acc == Access::ReadWrite)
    {
        InterruptLock lock;
        T current = *reinterpret_cast<volatile T*>(Address);
        *reinterpret_cast<volatile T*>(Address) = (current & ~clear_mask) | set_mask;
    }
};

// 4. Опис апаратної периферії GPIO
enum class Pin : uint8_t {
    P0 = 0, P1, P2, P3, P4, P5, P6, P7,
    P8, P9, P10, P11, P12, P13, P14, P15
};

enum class PinMode : uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

template <uintptr_t BaseAddress>
struct GpioPort {
    using Moder = Register<BaseAddress + 0x00, uint32_t, Access::ReadWrite>;
    using Idr   = Register<BaseAddress + 0x10, uint32_t, Access::ReadOnly>;
    using Odr   = Register<BaseAddress + 0x14, uint32_t, Access::ReadWrite>;

    template <Pin P, PinMode M>
    static constexpr void configure_mode() noexcept {
        constexpr uint32_t shift = static_cast<uint8_t>(P) * 2U;
        constexpr uint32_t clear_mask = 0b11U << shift;
        constexpr uint32_t set_mask = static_cast<uint32_t>(M) << shift;

        Moder::modify(clear_mask, set_mask);
    }

    template <Pin P>
    static inline void set_pin(bool high) noexcept {
        constexpr uint32_t mask = 1U << static_cast<uint8_t>(P);
        if (high) {
            Odr::set_bits(mask);
        } else {
            Odr::clear_bits(mask);
        }
    }

    template <Pin P>
    [[nodiscard]] static inline bool read_pin() noexcept {
        constexpr uint32_t mask = 1U << static_cast<uint8_t>(P);
        return (Idr::read() & mask) != 0;
    }
};

// Конкретний екземпляр порту GPIOA на шині AHB2
using GpioA = GpioPort<0x40020000UL>;

} // namespace mcu

// Приклад використання в коді прошивки
void configure_hardware() {
    mcu::GpioA::configure_mode<mcu::Pin::P5, mcu::PinMode::Output>();
    mcu::GpioA::set_pin<mcu::Pin::P5>(true);
}

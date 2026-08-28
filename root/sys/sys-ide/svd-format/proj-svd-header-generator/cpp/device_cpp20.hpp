/* Згенерований файл device_cpp20.hpp */
#ifndef __MICRO32_HAL_REGS_HPP__
#define __MICRO32_HAL_REGS_HPP__

#include <cstdint>
#include <cstddef>
#include <concepts>

namespace micro32::hal {

struct ReadOnlyPolicy {};
struct WriteOnlyPolicy {};
struct ReadWritePolicy {};

template <typename T>
concept Readable = std::same_as<T, ReadOnlyPolicy> || std::same_as<T, ReadWritePolicy>;

template <typename T>
concept Writable = std::same_as<T, WriteOnlyPolicy> || std::same_as<T, ReadWritePolicy>;

template <uint32_t Offset, uint32_t Width, typename ValueType = uint32_t>
struct BitField {
    static constexpr uint32_t pos = Offset;
    static constexpr uint32_t width = Width;
    static constexpr uint32_t mask = ((1UL << Width) - 1UL) << pos;

    [[nodiscard]] static constexpr uint32_t encode(ValueType val) noexcept {
        return (static_cast<uint32_t>(val) << pos) & mask;
    }

    [[nodiscard]] static constexpr ValueType decode(uint32_t reg_val) noexcept {
        return static_cast<ValueType>((reg_val & mask) >> pos);
    }
};

template <uintptr_t Address, typename AccessPolicy = ReadWritePolicy, typename RegType = uint32_t>
class Register {
public:
    static constexpr uintptr_t address = Address;

    [[nodiscard]] static inline RegType read() noexcept requires Readable<AccessPolicy> {
        return *reinterpret_cast<volatile RegType*>(address);
    }

    static inline void write(RegType val) noexcept requires Writable<AccessPolicy> {
        *reinterpret_cast<volatile RegType*>(address) = val;
    }

    template <typename Field, typename ValType>
    static inline void set_field(ValType val) noexcept requires Readable<AccessPolicy> && Writable<AccessPolicy> {
        RegType current = read();
        current &= ~Field::mask;
        current |= Field::encode(val);
        write(current);
    }
};

namespace usart1 {
    inline constexpr uintptr_t base_addr = 0x40013800UL;

    using SR = Register<base_addr + 0x0000UL, ReadWritePolicy, uint32_t>;
    struct SR_Fields {
        using RXNE = BitField<5, 1, bool>;
        using TC   = BitField<6, 1, bool>;
        using TXE  = BitField<7, 1, bool>;
    };

    using DR = Register<base_addr + 0x0004UL, ReadWritePolicy, uint32_t>;
    struct DR_Fields {
        using DATA = BitField<0, 9, uint32_t>;
    };

    using CR1 = Register<base_addr + 0x000CUL, ReadWritePolicy, uint32_t>;
    struct CR1_Fields {
        enum class M_Enum : uint32_t {
            M_8Bit = 0x0,
            M_9Bit = 0x1,
        };
        using UE = BitField<0, 1, bool>;
        using TE = BitField<3, 1, bool>;
        using M  = BitField<12, 1, M_Enum>;
    };
} // namespace usart1

namespace usart2 {
    inline constexpr uintptr_t base_addr = 0x40004400UL;
    using SR  = Register<base_addr + 0x0000UL, ReadWritePolicy, uint32_t>;
    using DR  = Register<base_addr + 0x0004UL, ReadWritePolicy, uint32_t>;
    using CR1 = Register<base_addr + 0x000CUL, ReadWritePolicy, uint32_t>;
} // namespace usart2

} // namespace micro32::hal

#endif /* __MICRO32_HAL_REGS_HPP__ */

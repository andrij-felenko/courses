// core/inc/compiler_port.hpp
#ifndef COMPILER_PORT_HPP
#define COMPILER_PORT_HPP

#include <cstdint>
#include <cstddef>
#include <span>

#if defined(__GNUC__) || defined(__clang__)
    #define PORT_RAMFUNC        [[gnu::section(".ramfunc"), gnu::noinline]]
    #define PORT_NORETURN       [[noreturn]]
    #define PORT_ALIGNED(n)     alignas(n)
    #define PORT_PACKED_STRUCT  struct [[gnu::packed]]
    #define PORT_WEAK           [[gnu::weak]]

    inline void port_barrier() noexcept { asm volatile("" ::: "memory"); }
    inline void port_nop() noexcept     { asm volatile("nop"); }

#elif defined(__ICCARM__)
    #define PORT_RAMFUNC        __ramfunc
    #define PORT_NORETURN       [[noreturn]]
    #define PORT_ALIGNED(n)     alignas(n)
    #define PORT_PACKED_STRUCT  __packed struct
    #define PORT_WEAK           __weak

    inline void port_barrier() noexcept { asm volatile("" ::: "memory"); }
    inline void port_nop() noexcept     { __no_operation(); }
#else
    #error "Невідомий компілятор: додайте відповідні макроси розширень"
#endif

namespace core::portable {

PORT_PACKED_STRUCT TelemetryFrame {
    std::uint32_t timestamp_ms;
    std::uint16_t voltage_mv;
    std::uint16_t current_ma;
    std::uint8_t  status_flags;
};

PORT_RAMFUNC void flash_critical_write_page(std::uint32_t page_addr,
                                            std::span<const std::uint8_t> payload) noexcept;

} // namespace core::portable

#endif // COMPILER_PORT_HPP

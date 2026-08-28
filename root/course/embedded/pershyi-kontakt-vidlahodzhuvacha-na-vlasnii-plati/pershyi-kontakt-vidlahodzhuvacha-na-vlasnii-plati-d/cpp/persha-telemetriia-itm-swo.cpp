// itm_debug.hpp — C++ обгортка для налагоджувального потоку ITM
#include <cstdint>
#include <string_view>

namespace debug {
    inline constexpr std::uintptr_t demcr_addr   = 0xE000EDFCU;
    inline constexpr std::uintptr_t itm_ter_addr = 0xE0000E00U;
    inline constexpr std::uintptr_t itm_tcr_addr = 0xE0000E80U;
    inline constexpr std::uintptr_t itm_port0_addr = 0xE0000000U;

    class ItmStream {
    public:
        static void init() noexcept {
            *reinterpret_cast<volatile std::uint32_t*>(demcr_addr) |= (1U << 24);
            *reinterpret_cast<volatile std::uint32_t*>(itm_tcr_addr) |= (1U << 0);
            *reinterpret_cast<volatile std::uint32_t*>(itm_ter_addr) |= (1U << 0);
        }

        static void write(char ch) noexcept {
            auto& demcr = *reinterpret_cast<volatile std::uint32_t*>(demcr_addr);
            auto& ter   = *reinterpret_cast<volatile std::uint32_t*>(itm_ter_addr);
            auto& port0 = *reinterpret_cast<volatile std::uint8_t*>(itm_port0_addr);

            if ((demcr & (1U << 24)) && (ter & (1U << 0))) {
                while (port0 == 0) {
                    asm volatile("nop");
                }
                port0 = static_cast<std::uint8_t>(ch);
            }
        }

        static void print(std::string_view text) noexcept {
            for (char ch : text) {
                write(ch);
            }
        }
    };
}

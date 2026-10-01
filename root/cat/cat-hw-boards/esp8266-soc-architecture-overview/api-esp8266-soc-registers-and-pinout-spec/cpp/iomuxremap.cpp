#include <cstdint>

constexpr uintptr_t REG_IOMUX_BASE        = 0x60000800;
constexpr uintptr_t PERIPHS_IO_MUX_MTCK_U = REG_IOMUX_BASE + 0x08; // GPIO13 / HSPI_MOSI
constexpr uintptr_t PERIPHS_IO_MUX_MTMS_U = REG_IOMUX_BASE + 0x0C; // GPIO14 / HSPI_CLK

constexpr uint32_t FUNC_MASK              = ~(0x7U << 4);
constexpr uint32_t FUNC_HSPI              = (0x2U << 4);

class IomuxRemap {
public:
    static void set_hspi_alternate_pins() {
        auto* reg_mtck = reinterpret_cast<volatile uint32_t*>(PERIPHS_IO_MUX_MTCK_U);
        auto* reg_mtms = reinterpret_cast<volatile uint32_t*>(PERIPHS_IO_MUX_MTMS_U);

        *reg_mtck = (*reg_mtck & FUNC_MASK) | FUNC_HSPI;
        *reg_mtms = (*reg_mtms & FUNC_MASK) | FUNC_HSPI;
    }
};

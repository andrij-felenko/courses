#include <cstdint>
#include <utility>

namespace embedded::hardware {

/* Шаблонний драйвер периферійного прискорювача CORDIC */
template <uintptr_t BaseAddress>
class CordicDriver {
private:
    struct Registers {
        volatile uint32_t CSR;
        volatile uint32_t WDATA;
        volatile uint32_t RDATA;
    };

    static constexpr auto Regs = reinterpret_cast<Registers*>(BaseAddress);

    static constexpr uint32_t ModeCosSin      = 0x00000000U;
    static constexpr uint32_t ModeModPhase    = 0x00000002U;
    static constexpr uint32_t Precision24     = 0x00000050U;
    static constexpr uint32_t FlagResultReady = 0x80000000U;

public:
    struct TrigonometricPair {
        int32_t cos_val;
        int32_t sin_val;
    };

    struct PackedResultQ15 {
        int16_t cos_val;
        int16_t sin_val;
    };

    /* Ініціалізація апаратного конвеєра прискорювача */
    static void init() noexcept {
        Regs->CSR = ModeCosSin | Precision24;
    }

    /* Безпечне виконання тригонометричного розрахунку для 32-бітних даних */
    [[nodiscard]] static TrigonometricPair calculateSinCos(int32_t angle_bam) noexcept {
        Regs->WDATA = static_cast<uint32_t>(angle_bam);

        /* Апаратні цикли очікування утримують шину до готовності результату */
        const auto cos_res = static_cast<int32_t>(Regs->RDATA);
        const auto sin_res = static_cast<int32_t>(Regs->RDATA);

        return TrigonometricPair{cos_res, sin_res};
    }

    /* Упакований розрахунок пари функцій у форматі Q1.15 */
    [[nodiscard]] static PackedResultQ15 calculatePackedQ15(int16_t angle_bam) noexcept {
        Regs->WDATA = static_cast<uint32_t>(static_cast<uint16_t>(angle_bam));

        const uint32_t packed = Regs->RDATA;
        return PackedResultQ15{
            static_cast<int16_t>(packed & 0xFFFFU),
            static_cast<int16_t>((packed >> 16) & 0xFFFFU)
        };
    }

    /* Перевірка стану готовності обчислювального вузла */
    [[nodiscard]] static bool isDataReady() noexcept {
        return (Regs->CSR & FlagResultReady) != 0U;
    }
};

/* Спеціалізація драйвера для фізичного адреса периферійного блоку мікроконтролера */
using Cordic = CordicDriver<0x40020C00UL>;

} /* namespace embedded::hardware */

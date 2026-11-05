#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace daplink::hw {

constexpr std::uintptr_t FlashRegAcr  = 0x40023C00U;
constexpr std::uintptr_t FlashRegKeyr = 0x40023C04U;
constexpr std::uintptr_t FlashRegSr   = 0x40023C0CU;
constexpr std::uintptr_t FlashRegCr   = 0x40023C10U;

constexpr std::uint32_t Key1          = 0x45670123U;
constexpr std::uint32_t Key2          = 0xCDEF89ABU;

constexpr std::uint32_t CrPg          = (1U << 0);
constexpr std::uint32_t CrSer         = (1U << 1);
constexpr std::uint32_t CrStrt        = (1U << 16);
constexpr std::uint32_t CrLock        = (1U << 31);
constexpr std::uint32_t CrSnbPos      = 3U;
constexpr std::uint32_t CrSnbMask     = (0x1FU << CrSnbPos);

constexpr std::uint32_t SrBsy         = (1U << 16);
constexpr std::uint32_t SrPgSerr      = (1U << 7);
constexpr std::uint32_t SrWrpErr      = (1U << 4);

constexpr std::uint32_t AcrIcen       = (1U << 9);
constexpr std::uint32_t AcrDcen       = (1U << 10);
constexpr std::uint32_t AcrIcrst      = (1U << 11);
constexpr std::uint32_t AcrDcrst      = (1U << 12);

constexpr std::size_t   LbaSectorBytes = 512U;
constexpr std::size_t   FlashSectorBytes = 2048U;

enum class BufferState : std::uint8_t {
    Empty,
    Filling,
    Ready,
    Writing
};

// RAII обгортка для безпечного розблокування контролера Flash
class FlashUnlockGuard {
public:
    FlashUnlockGuard() noexcept {
        auto& cr = *reinterpret_cast<volatile std::uint32_t*>(FlashRegCr);
        if ((cr & CrLock) != 0U) {
            *reinterpret_cast<volatile std::uint32_t*>(FlashRegKeyr) = Key1;
            *reinterpret_cast<volatile std::uint32_t*>(FlashRegKeyr) = Key2;
        }
    }
    ~FlashUnlockGuard() noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(FlashRegCr) |= CrLock;
    }
    FlashUnlockGuard(const FlashUnlockGuard&) = delete;
    FlashUnlockGuard& operator=(const FlashUnlockGuard&) = delete;
};

class FlashController {
public:
    static void flushCache() noexcept {
        auto& acr = *reinterpret_cast<volatile std::uint32_t*>(FlashRegAcr);
        acr &= ~(AcrIcen | AcrDcen);
        acr |= (AcrIcrst | AcrDcrst);
        acr &= ~(AcrIcrst | AcrDcrst);
        acr |= (AcrIcen | AcrDcen);
    }

    [[nodiscard]] static bool waitReady() noexcept {
        auto& sr = *reinterpret_cast<volatile std::uint32_t*>(FlashRegSr);
        while ((sr & SrBsy) != 0U) {
            // Скидання сторожового таймера
        }
        if ((sr & (SrPgSerr | SrWrpErr)) != 0U) {
            sr |= (SrPgSerr | SrWrpErr);
            return false;
        }
        return true;
    }

    [[nodiscard]] static bool eraseSector(std::uint8_t sectorIndex) noexcept {
        FlashUnlockGuard lockGuard;
        if (!waitReady()) {
            return false;
        }
        auto& cr = *reinterpret_cast<volatile std::uint32_t*>(FlashRegCr);
        cr &= ~CrSnbMask;
        cr |= CrSer | (static_cast<std::uint32_t>(sectorIndex) << CrSnbPos);
        cr |= CrStrt;

        const bool result = waitReady();
        cr &= ~CrSer;
        flushCache();
        return result;
    }

    [[nodiscard]] static bool programWord(std::uintptr_t address, std::uint32_t word) noexcept {
        FlashUnlockGuard lockGuard;
        if (!waitReady()) {
            return false;
        }
        auto& cr = *reinterpret_cast<volatile std::uint32_t*>(FlashRegCr);
        cr |= CrPg;
        *reinterpret_cast<volatile std::uint32_t*>(address) = word;

        const bool result = waitReady();
        cr &= ~CrPg;
        return result;
    }
};

class AsyncDoubleBufferPipeline {
public:
    struct BufferSlot {
        std::array<std::uint8_t, LbaSectorBytes> storage{};
        volatile BufferState state{BufferState::Empty};
        std::uint32_t offset{0};
    };

    bool receiveUsbPacket(std::span<const std::uint8_t> packet, std::uint32_t offset) noexcept {
        auto& buf = m_slots[m_rxIdx];
        if (buf.state != BufferState::Empty) {
            return false;
        }
        buf.state = BufferState::Filling;
        buf.offset = offset;
        std::copy(packet.begin(), packet.end(), buf.storage.begin());
        buf.state = BufferState::Ready;
        m_rxIdx = (m_rxIdx == 0U) ? 1U : 0U;
        return true;
    }

    void processFlashQueue(std::uintptr_t appBase) noexcept {
        auto& buf = m_slots[m_flashIdx];
        if (buf.state == BufferState::Ready) {
            buf.state = BufferState::Writing;
            const std::uintptr_t targetAddr = appBase + buf.offset;

            if ((targetAddr % FlashSectorBytes) == 0U) {
                const auto sector = static_cast<std::uint8_t>(buf.offset / FlashSectorBytes);
                FlashController::eraseSector(sector);
            }

            const auto* words = reinterpret_cast<const std::uint32_t*>(buf.storage.data());
            for (std::size_t i = 0; i < (LbaSectorBytes / sizeof(std::uint32_t)); ++i) {
                FlashController::programWord(targetAddr + (i * sizeof(std::uint32_t)), words[i]);
            }

            buf.state = BufferState::Empty;
            m_flashIdx = (m_flashIdx == 0U) ? 1U : 0U;
        }
    }

    [[nodiscard]] bool isThrottleRequired() const noexcept {
        return m_slots[m_rxIdx].state != BufferState::Empty;
    }

private:
    std::array<BufferSlot, 2> m_slots{};
    std::uint8_t m_rxIdx{0};
    std::uint8_t m_flashIdx{0};
};

} // namespace daplink::hw

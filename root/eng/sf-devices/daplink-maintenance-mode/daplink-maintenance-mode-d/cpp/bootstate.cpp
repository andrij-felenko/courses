#include <cstdint>
#include <cstddef>
#include <span>

namespace daplink {

constexpr std::uintptr_t SramBaseAddr       = 0x20000000U;
constexpr std::size_t    SramSizeBytes      = 32U * 1024U;
constexpr std::uintptr_t FlashAppStartAddr  = 0x00008000U;
constexpr std::uintptr_t FlashAppEndAddr    = 0x00020000U;
constexpr std::size_t    FlashSectorSize    = 2048U;
constexpr std::uint32_t  MaintenanceMagic   = 0x544E4941U;
constexpr std::uintptr_t ScbVtorAddr        = 0xE000ED08U;

enum class BootState : std::uint8_t {
    Init,
    CheckTrigger,
    MaintenanceRun,
    VerifyAndBoot
};

struct VectorTable {
    std::uint32_t initialMsp;
    std::uint32_t resetHandler;
};

// Інтерфейс апаратного рівня мікроконтролера
class IHardwareDriver {
public:
    virtual ~IHardwareDriver() = default;
    virtual bool isButtonPressed() const = 0;
    virtual void feedWatchdog() = 0;
    virtual bool eraseSector(std::uintptr_t sectorAddr) = 0;
    virtual bool writeFlashBlock(std::uintptr_t destAddr, std::span<const std::uint8_t> data) = 0;
    virtual void disconnectUsb() = 0;
    virtual void systemReset() = 0;
};

class MaintenanceManager {
public:
    explicit MaintenanceManager(IHardwareDriver& hw, volatile std::uint32_t& sharedFlag)
        : m_hw(hw), m_sharedFlag(sharedFlag), m_state(BootState::Init) {}

    // Верифікація векторів перед запуском робочої прошивки
    [[nodiscard]] static bool isApplicationValid(std::uintptr_t appAddr) noexcept {
        const auto* vt = reinterpret_cast<const VectorTable*>(appAddr);
        if (vt->initialMsp < SramBaseAddr || vt->initialMsp > (SramBaseAddr + SramSizeBytes)) {
            return false;
        }
        if (vt->resetHandler < appAddr || vt->resetHandler >= FlashAppEndAddr) {
            return false;
        }
        return (vt->resetHandler & 0x01U) != 0U;
    }

    // Запис блоку даних при перетягуванні файлу
    [[nodiscard]] bool writeLbaPayload(std::uint32_t offset, std::span<const std::uint8_t> payload) {
        const std::uintptr_t targetAddr = FlashAppStartAddr + offset;
        if (targetAddr + payload.size() > FlashAppEndAddr) {
            return false;
        }
        m_hw.feedWatchdog();
        if ((targetAddr % FlashSectorSize) == 0U) {
            if (!m_hw.eraseSector(targetAddr)) {
                return false;
            }
        }
        return m_hw.writeFlashBlock(targetAddr, payload);
    }

    // Перехід у робочу програму із переналаштуванням VTOR
    [[noreturn]] void jumpToApplication(std::uintptr_t appAddr) {
        const auto* vt = reinterpret_cast<const VectorTable*>(appAddr);
        m_hw.disconnectUsb();
        asm volatile ("cpsid i" : : : "memory");

        auto* vtor = reinterpret_cast<volatile std::uint32_t*>(ScbVtorAddr);
        *vtor = appAddr;

        asm volatile (
            "msr msp, %0
"
            "bx %1
"
            : : "r"(vt->initialMsp), "r"(vt->resetHandler) : "memory"
        );
        __builtin_unreachable();
    }

    void run() {
        bool enterMaintenance = false;
        while (true) {
            m_hw.feedWatchdog();
            switch (m_state) {
            case BootState::Init:
                m_state = BootState::CheckTrigger;
                break;
            case BootState::CheckTrigger:
                if (m_hw.isButtonPressed() || (m_sharedFlag == MaintenanceMagic)) {
                    m_sharedFlag = 0U;
                    enterMaintenance = true;
                }
                if (!isApplicationValid(FlashAppStartAddr)) {
                    enterMaintenance = true;
                }
                m_state = enterMaintenance ? BootState::MaintenanceRun : BootState::VerifyAndBoot;
                break;
            case BootState::MaintenanceRun:
                break;
            case BootState::VerifyAndBoot:
                if (isApplicationValid(FlashAppStartAddr)) {
                    jumpToApplication(FlashAppStartAddr);
                }
                m_state = BootState::MaintenanceRun;
                break;
            }
        }
    }

private:
    IHardwareDriver& m_hw;
    volatile std::uint32_t& m_sharedFlag;
    BootState m_state;
};

} // namespace daplink

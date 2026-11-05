#include <cstdint>
#include <cstddef>
#include <array>
#include <string_view>

namespace embedded::diagnostics {

enum class BootPhase : uint8_t {
    Candidate = 0,
    Testing,
    Confirmed,
    RollbackRequired
};

struct alignas(4) CpuContextRecord {
    uint32_t signature;
    uint32_t r0, r1, r2, r3, r12, lr, pc, psr;
    uint32_t cfsr, hfsr, mmar, bfar;
    uint32_t checksum;
};

class alignas(32) RttNonBlockingChannel final {
public:
    static constexpr std::size_t kCapacity = 512;

    void log(std::string_view msg) noexcept {
        for (char ch : msg) {
            const std::size_t next_head = (head_ + 1U) % kCapacity;
            if (next_head != tail_) {
                storage_[head_] = ch;
                head_ = next_head;
            } else {
                break; /* Буфер повний, відкидаємо для збереження детермінізму */
            }
        }
    }

private:
    std::array<char, kCapacity> storage_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
};

class TrialBootSupervisor final {
public:
    static constexpr uint32_t kBootMetaMagic = 0x54524941U; /* "TRIA" */

    struct Metadata {
        uint32_t magic;
        BootPhase phase;
        uint8_t  attempts_remaining;
        uint16_t reserved;
    };

    explicit TrialBootSupervisor(Metadata& meta, RttNonBlockingChannel& logger) noexcept
        : meta_(meta), logger_(logger) {}

    [[nodiscard]] bool check_boot_viability() noexcept {
        if (meta_.phase == BootPhase::Confirmed) {
            return true;
        }

        if (meta_.phase == BootPhase::Candidate) {
            meta_.phase = BootPhase::Testing;
            meta_.attempts_remaining = 3;
            logger_.log("[BOOT] Початок випробувального тестування кандидата");
            return true;
        }

        if (meta_.phase == BootPhase::Testing) {
            if (meta_.attempts_remaining > 1) {
                meta_.attempts_remaining--;
                logger_.log("[BOOT] Повторна спроба після збою, лічильник зменшено");
                return true;
            }
            meta_.phase = BootPhase::RollbackRequired;
            logger_.log("[BOOT] Спроби вичерпано. Потрібен відкат прошивки!");
            return false;
        }

        return false;
    }

    void mark_as_stable() noexcept {
        meta_.phase = BootPhase::Confirmed;
        meta_.attempts_remaining = 0;
        logger_.log("[BOOT] Образ підтверджено. Робочий розділ зафіксовано");
    }

    [[nodiscard]] bool is_rollback_needed() const noexcept {
        return meta_.phase == BootPhase::RollbackRequired;
    }

private:
    Metadata& meta_;
    RttNonBlockingChannel& logger_;
};

class FaultRecorder final {
public:
    static constexpr uint32_t kDumpMagic = 0xDEADBEEFU;

    static void capture_from_stack(const uint32_t* stack_frame, CpuContextRecord& out) noexcept {
        volatile const uint32_t* const cfsr = reinterpret_cast<volatile uint32_t*>(0xE000ED28U);
        volatile const uint32_t* const hfsr = reinterpret_cast<volatile uint32_t*>(0xE000ED2CU);
        volatile const uint32_t* const mmar = reinterpret_cast<volatile uint32_t*>(0xE000ED34U);
        volatile const uint32_t* const bfar = reinterpret_cast<volatile uint32_t*>(0xE000ED38U);

        out.signature = kDumpMagic;
        out.r0 = stack_frame[0];
        out.r1 = stack_frame[1];
        out.r2 = stack_frame[2];
        out.r3 = stack_frame[3];
        out.r12 = stack_frame[4];
        out.lr = stack_frame[5];
        out.pc = stack_frame[6];
        out.psr = stack_frame[7];

        out.cfsr = *cfsr;
        out.hfsr = *hfsr;
        out.mmar = *mmar;
        out.bfar = *bfar;

        out.checksum = compute_checksum(out);
    }

private:
    static uint32_t compute_checksum(const CpuContextRecord& rec) noexcept {
        const auto* words = reinterpret_cast<const uint32_t*>(&rec);
        uint32_t sum = 0;
        constexpr std::size_t count = (sizeof(CpuContextRecord) / sizeof(uint32_t)) - 1U;
        for (std::size_t i = 0; i < count; ++i) {
            sum ^= words[i];
        }
        return sum;
    }
};

} // namespace embedded::diagnostics

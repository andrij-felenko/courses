#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <cstdint>
#include <format>
#include <span>

namespace ReleaseEngineering {

struct Budgets {
    static constexpr uint32_t MaxFlashBytes = 8 * 1024 * 1024 + 512 * 1024; // 8.5 MiB
    static constexpr uint32_t MaxRamBytes = 384 * 1024;                     // 384 KiB
    static constexpr uint32_t MaxBootTimeMs = 250;
    static constexpr float MaxSleepCurrentMicroAmps = 15.0f;
    static constexpr uint32_t MaxAllowedBlockers = 0;
};

struct CandidateMetrics {
    uint32_t flashUsedBytes{0};
    uint32_t ramUsedBytes{0};
    uint32_t bootTimeMs{0};
    float sleepCurrentMicroAmps{0.0f};
    uint32_t hilTotalTests{0};
    uint32_t hilPassedTests{0};
    uint32_t criticalDefectsCount{0};
    bool hardfaultOccurred{false};
    bool watchdogResetOccurred{false};
};

enum class RejectionReason {
    CriticalBugsPresent,
    FatalHardwareFault,
    HilTestsIncomplete,
    FlashOverrun,
    RamOverrun,
    PowerBudgetExceeded,
    BootTimeExceeded
};

struct PromotionCertificate {
    std::string releaseTag;
    std::string sha256Hash;
    std::string approvalSummary;
};

class QualityGateArbiter {
public:
    static std::expected<PromotionCertificate, std::pair<RejectionReason, std::string>>
    evaluate(std::string_view releaseTag,
             std::string_view sha256Hash,
             const CandidateMetrics& m) noexcept {
        
        // 1. Нульовий рівень критичних багів
        if (m.criticalDefectsCount > Budgets::MaxAllowedBlockers) {
            return std::unexpected(std::make_pair(
                RejectionReason::CriticalBugsPresent,
                std::format("Знайдено {} критичних багів при ліміті {}",
                            m.criticalDefectsCount, Budgets::MaxAllowedBlockers)
            ));
        }

        // 2. Відсутність апаратних панік
        if (m.hardfaultOccurred || m.watchdogResetOccurred) {
            return std::unexpected(std::make_pair(
                RejectionReason::FatalHardwareFault,
                std::format("Зафіксовано апаратний збій (HardFault={}, WDT={})",
                            m.hardfaultOccurred, m.watchdogResetOccurred)
            ));
        }

        // 3. 100% проходження HIL
        if (m.hilTotalTests == 0 || m.hilPassedTests < m.hilTotalTests) {
            return std::unexpected(std::make_pair(
                RejectionReason::HilTestsIncomplete,
                std::format("HIL верифікація неповна: {}/{} успішно",
                            m.hilPassedTests, m.hilTotalTests)
            ));
        }

        // 4. Перевірка обсягів пам'яті
        if (m.flashUsedBytes > Budgets::MaxFlashBytes) {
            return std::unexpected(std::make_pair(
                RejectionReason::FlashOverrun,
                std::format("Flash ROM {} перевищує ліміт {}",
                            m.flashUsedBytes, Budgets::MaxFlashBytes)
            ));
        }

        if (m.ramUsedBytes > Budgets::MaxRamBytes) {
            return std::unexpected(std::make_pair(
                RejectionReason::RamOverrun,
                std::format("SRAM {} перевищує ліміт {}",
                            m.ramUsedBytes, Budgets::MaxRamBytes)
            ));
        }

        // 5. Енергетичний та часовий бюджет
        if (m.sleepCurrentMicroAmps > Budgets::MaxSleepCurrentMicroAmps) {
            return std::unexpected(std::make_pair(
                RejectionReason::PowerBudgetExceeded,
                std::format("Струм сну {:.2f} uA > {:.2f} uA ліміту",
                            m.sleepCurrentMicroAmps, Budgets::MaxSleepCurrentMicroAmps)
            ));
        }

        if (m.bootTimeMs > Budgets::MaxBootTimeMs) {
            return std::unexpected(std::make_pair(
                RejectionReason::BootTimeExceeded,
                std::format("Час старту {} мс > {} мс ліміту",
                            m.bootTimeMs, Budgets::MaxBootTimeMs)
            ));
        }

        return PromotionCertificate{
            .releaseTag = std::string(releaseTag),
            .sha256Hash = std::string(sha256Hash),
            .approvalSummary = "Усі критерії виходу виконано на 100%. Готово до підпису GA."
        };
    }
};

} // namespace ReleaseEngineering

int main() {
    using namespace ReleaseEngineering;

    CandidateMetrics metrics{
        .flashUsedBytes = 4194304,
        .ramUsedBytes = 196608,
        .bootTimeMs = 180,
        .sleepCurrentMicroAmps = 11.4f,
        .hilTotalTests = 1450,
        .hilPassedTests = 1450,
        .criticalDefectsCount = 0,
        .hardfaultOccurred = false,
        .watchdogResetOccurred = false
    };

    auto result = QualityGateArbiter::evaluate(
        "v2.4.0-rc.3",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        metrics
    );

    if (result.has_value()) {
        const auto& cert = result.value();
        std::cout << "=== СЕРТИФІКАТ ПРОМОЦІЇ GA ===\n";
        std::cout << "Тег релізу : " << cert.releaseTag << "\n";
        std::cout << "SHA-256    : " << cert.sha256Hash << "\n";
        std::cout << "Підсумок   : " << cert.approvalSummary << "\n";
        return 0;
    } else {
        const auto& [err, msg] = result.error();
        std::cerr << "=== ВІДХИЛЕННЯ РЕЛІЗ-КАНДИДАТА ===\n";
        std::cerr << "Причина: " << msg << "\n";
        return 1;
    }
}

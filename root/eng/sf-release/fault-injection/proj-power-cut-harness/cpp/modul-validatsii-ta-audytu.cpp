#include <string_view>
#include <string>
#include <optional>
#include <format>
#include <iostream>

namespace HarnessAudit {

enum class VerdictStatus {
    OkRecovered,
    BrickedBootloop,
    SilentCorruption,
    TimeoutNoResponse
};

struct AuditResult {
    std::uint32_t  runIndex{0};
    std::uint32_t  cutDelayUs{0};
    VerdictStatus  status{VerdictStatus::TimeoutNoResponse};
    std::string    description{};
};

class TargetLogAnalyzer {
public:
    [[nodiscard]] static AuditResult evaluateLog(std::string_view consoleOutput, std::uint32_t runIdx, std::uint32_t delayUs) noexcept {
        AuditResult res;
        res.runIndex = runIdx;
        res.cutDelayUs = delayUs;

        if (consoleOutput.empty()) {
            res.status = VerdictStatus::TimeoutNoResponse;
            res.description = "Цільовий пристрій не надав консольного виводу після рестарту";
            return res;
        }

        if (consoleOutput.contains("HardFault_Handler") || consoleOutput.contains("PANIC:") || consoleOutput.contains("ASSERT_FAILED")) {
            res.status = VerdictStatus::BrickedBootloop;
            res.description = "Паніка ядра або HardFault під час ініціалізації завантажувача";
            return res;
        }

        if (consoleOutput.contains("lfs_mount: corrupt") || consoleOutput.contains("CRC_MISMATCH_FATAL")) {
            res.status = VerdictStatus::SilentCorruption;
            res.description = "Невідновне пошкодження метаданих або метастабільні байти Flash";
            return res;
        }

        if (consoleOutput.contains("BOOT_OK") || consoleOutput.contains("ROLLBACK_OK") || consoleOutput.contains("TRANSACTION_REPLAY_SUCCESS")) {
            res.status = VerdictStatus::OkRecovered;
            res.description = "Коректне атомарне відновлення стану або відкат на резервний банк";
            return res;
        }

        res.status = VerdictStatus::SilentCorruption;
        res.description = "Нерозпізнаний стан системи: відсутній маркер успішного завантаження";
        return res;
    }
};

} // namespace HarnessAudit

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <iomanip>
#include <span>
#include <format>
#include <memory>
#include <cstdint>

enum class DefectSeverity {
    Minor,
    Major,
    Critical
};

enum class DefectCategory {
    Logic,
    Concurrency,
    HardwareInterface,
    ResourceSafety,
    StandardsCompliance
};

enum class DetectionPhase {
    Preparation,
    Meeting
};

enum class ArtifactType {
    EmbeddedCode,
    Schematic,
    PcbLayout
};

enum class ExitDecision {
    Passed,
    ReworkAndVerify,
    ReInspect
};

struct DefectRecord {
    std::string location;
    int line_or_refdes{0};
    DefectSeverity severity{DefectSeverity::Minor};
    DefectCategory category{DefectCategory::Logic};
    DetectionPhase phase{DetectionPhase::Meeting};
    std::string description;
};

struct InspectionMetrics {
    double inspection_rate_per_hour{0.0};
    double defect_density_per_kloc{0.0};
    double weighted_defect_score{0.0};
    std::size_t critical_count{0};
    std::size_t major_count{0};
    std::size_t minor_count{0};
    std::size_t prep_findings{0};
    std::size_t meeting_findings{0};
    ExitDecision decision{ExitDecision::Passed};
    bool rate_warning{false};
};

class FaganInspectionSession {
public:
    FaganInspectionSession(std::string_view artifact_name,
                           std::string_view author,
                           std::string_view moderator,
                           std::string_view reader,
                           ArtifactType type,
                           std::size_t size_units,
                           double meeting_minutes)
        : artifact_name_(artifact_name),
          author_(author),
          moderator_(moderator),
          reader_(reader),
          artifact_type_(type),
          artifact_size_units_(size_units),
          meeting_duration_minutes_(meeting_minutes) {}

    void add_inspector(std::string_view inspector_name) {
        inspectors_.emplace_back(inspector_name);
    }

    void add_prep_time(double person_hours) noexcept {
        if (person_hours > 0.0) {
            prep_time_person_hours_ += person_hours;
        }
    }

    void record_defect(std::string_view location,
                       int line_or_refdes,
                       DefectSeverity severity,
                       DefectCategory category,
                       DetectionPhase phase,
                       std::string_view description) {
        defects_.push_back(DefectRecord{
            .location = std::string(location),
            .line_or_refdes = line_or_refdes,
            .severity = severity,
            .category = category,
            .phase = phase,
            .description = std::string(description)
        });
    }

    [[nodiscard]] std::optional<InspectionMetrics> compute_metrics() const noexcept {
        if (artifact_size_units_ == 0) {
            return std::nullopt;
        }

        InspectionMetrics m;

        if (meeting_duration_minutes_ > 0.0) {
            m.inspection_rate_per_hour =
                (static_cast<double>(artifact_size_units_) * 60.0) / meeting_duration_minutes_;
        }

        if (m.inspection_rate_per_hour > 220.0 || m.inspection_rate_per_hour < 40.0) {
            m.rate_warning = true;
        }

        for (const auto& d : defects_) {
            switch (d.severity) {
                case DefectSeverity::Critical:
                    m.critical_count++;
                    m.weighted_defect_score += 10.0;
                    break;
                case DefectSeverity::Major:
                    m.major_count++;
                    m.weighted_defect_score += 3.0;
                    break;
                case DefectSeverity::Minor:
                    m.minor_count++;
                    m.weighted_defect_score += 1.0;
                    break;
            }

            if (d.phase == DetectionPhase::Preparation) {
                m.prep_findings++;
            } else {
                m.meeting_findings++;
            }
        }

        m.defect_density_per_kloc =
            (static_cast<double>(defects_.size()) * 1000.0) / static_cast<double>(artifact_size_units_);

        if (m.critical_count > 0 || m.weighted_defect_score >= 25.0) {
            m.decision = ExitDecision::ReInspect;
        } else if (m.major_count > 0 || m.minor_count > 0) {
            m.decision = ExitDecision::ReworkAndVerify;
        } else {
            m.decision = ExitDecision::Passed;
        }

        return m;
    }

    void render_summary(std::ostream& os) const {
        auto metrics_opt = compute_metrics();
        if (!metrics_opt) {
            os << "Помилка обчислення метрик: нульовий розмір артефакту.\n";
            return;
        }
        const auto& m = *metrics_opt;

        os << "================================================================================\n";
        os << "                  ПРОТОКОЛ ФОРМАЛЬНОЇ ІНСПЕКЦІЇ ФАГАНА (C++20)                 \n";
        os << "================================================================================\n";
        os << "Артефакт:        " << artifact_name_ << "\n";
        os << "Автор:           " << author_ << "\n";
        os << "Модератор:       " << moderator_ << "\n";
        os << "Читець:          " << reader_ << "\n";
        os << "Інспектори:      ";
        for (std::size_t i = 0; i < inspectors_.size(); ++i) {
            os << inspectors_[i] << (i + 1 == inspectors_.size() ? "" : ", ");
        }
        os << "\n";
        os << "Розмір об'єкта:  " << artifact_size_units_ << " "
           << (artifact_type_ == ArtifactType::EmbeddedCode ? "LOC" : "Компонентів") << "\n";
        os << "Час засідання:   " << meeting_duration_minutes_ << " хв | Підготовка: "
           << prep_time_person_hours_ << " людино-годин\n";
        os << "--------------------------------------------------------------------------------\n";
        os << "МЕТРИКИ:\n";
        os << "  Швидкість:     " << std::fixed << std::setprecision(1)
           << m.inspection_rate_per_hour << " од/год "
           << (m.rate_warning ? "[УВАГА: темп поза оптимальними межами 100-150!]" : "[НОРМА]") << "\n";
        os << "  Дефекти:       " << defects_.size() << " (Підготовка: " << m.prep_findings
           << ", Засідання: " << m.meeting_findings << ")\n";
        os << "  Розподіл:      CRITICAL: " << m.critical_count
           << " | MAJOR: " << m.major_count
           << " | MINOR: " << m.minor_count << "\n";
        os << "  Щільність:     " << std::setprecision(2) << m.defect_density_per_kloc << " def / KLOC\n";
        os << "  Зважений бал:  " << std::setprecision(1) << m.weighted_defect_score << "\n";
        os << "--------------------------------------------------------------------------------\n";
        os << "РІШЕННЯ ВИХОДУ: " << decision_to_string(m.decision) << "\n";
        os << "================================================================================\n";
        os << "СПИСОК ДЕФЕКТІВ:\n";
        for (std::size_t i = 0; i < defects_.size(); ++i) {
            const auto& d = defects_[i];
            os << "[" << std::setw(2) << std::setfill('0') << (i + 1) << "] "
               << std::setw(8) << std::setfill(' ') << severity_to_string(d.severity) << " | "
               << std::setw(20) << category_to_string(d.category) << " | "
               << d.location << ":" << d.line_or_refdes << "\n"
               << "     Опис: " << d.description << "\n";
        }
        os << "================================================================================\n";
    }

private:
    static std::string_view severity_to_string(DefectSeverity sev) noexcept {
        switch (sev) {
            case DefectSeverity::Critical: return "CRITICAL";
            case DefectSeverity::Major:    return "MAJOR";
            case DefectSeverity::Minor:    return "MINOR";
        }
        return "UNKNOWN";
    }

    static std::string_view category_to_string(DefectCategory cat) noexcept {
        switch (cat) {
            case DefectCategory::Logic:               return "Logic/Algorithm";
            case DefectCategory::Concurrency:         return "Concurrency/ISR";
            case DefectCategory::HardwareInterface:    return "Hardware Interface";
            case DefectCategory::ResourceSafety:      return "Resource Safety";
            case DefectCategory::StandardsCompliance: return "Standards/MISRA";
        }
        return "Unknown";
    }

    static std::string_view decision_to_string(ExitDecision dec) noexcept {
        switch (dec) {
            case ExitDecision::Passed:          return "PASSED (Artifact Approved)";
            case ExitDecision::ReworkAndVerify: return "REWORK (Verify fixes by Moderator)";
            case ExitDecision::ReInspect:       return "RE-INSPECT (Mandatory Full Re-session)";
        }
        return "UNKNOWN";
    }

    std::string artifact_name_;
    std::string author_;
    std::string moderator_;
    std::string reader_;
    std::vector<std::string> inspectors_;
    ArtifactType artifact_type_{ArtifactType::EmbeddedCode};
    std::size_t artifact_size_units_{0};
    double prep_time_person_hours_{0.0};
    double meeting_duration_minutes_{0.0};
    std::vector<DefectRecord> defects_;
};

int main() {
    FaganInspectionSession session(
        "drivers/spi_dma_stm32f4.cpp",
        "О. Ковальчук (Firmware)",
        "І. Бондар (Lead Moderator)",
        "В. Ткаченко (Reader)",
        ArtifactType::EmbeddedCode,
        380,
        150.0
    );

    session.add_inspector("М. Шевченко (Safety Engineer)");
    session.add_inspector("Д. Мельник (Hardware Architect)");
    session.add_prep_time(3.5);

    session.record_defect(
        "spi_dma_stm32f4.cpp", 142,
        DefectSeverity::Critical,
        DefectCategory::Concurrency,
        DetectionPhase::Preparation,
        "Відсутній memory barrier перед запуском DMA; гонка кешу та пам'яті"
    );

    session.record_defect(
        "spi_dma_stm32f4.cpp", 89,
        DefectSeverity::Major,
        DefectCategory::HardwareInterface,
        DetectionPhase::Meeting,
        "Не скидається прапорець TXE перед читанням RXNE на шині SPI; зависання"
    );

    session.record_defect(
        "spi_dma_stm32f4.cpp", 215,
        DefectSeverity::Minor,
        DefectCategory::StandardsCompliance,
        DetectionPhase::Preparation,
        "Порушення MISRA Rule 10.4: неявне приведення знакового int до uint32_t"
    );

    session.render_summary(std::cout);
    return 0;
}

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <algorithm>
#include <iomanip>
#include <expected>

namespace SysNotary::CounterfeitMitigation {

enum class InspectionLevel {
    PackagingDocs = 1,
    OpticalSolvent = 2,
    XrayXrf = 3,
    DecapDie = 4,
    ElectricalAsa = 5
};

enum class CounterfeitDefectType {
    None = 0,
    BlacktoppingDetected,
    SolventMarkRemoved,
    Pin1IndentModified,
    XrayDieSizeMismatch,
    XrayBondWireDefect,
    XrfLeadRohsViolation,
    DecapDieLogoAbsent,
    DecapWrongMaskId,
    AsaSignatureFailed,
    QuiescentCurrentHigh
};

enum class LotDisposition {
    Accept,
    SuspectHold,
    QuarantineReject
};

struct SampleTestRecord {
    uint32_t sample_id{0};
    InspectionLevel level{InspectionLevel::PackagingDocs};
    CounterfeitDefectType defect{CounterfeitDefectType::None};
    float measured_metric{0.0f};
    std::string notes;
};

class LotInspectionDossier {
private:
    std::string lot_number_;
    std::string part_number_;
    std::string manufacturer_;
    uint32_t lot_size_{0};
    uint32_t sample_size_{0};
    std::vector<SampleTestRecord> records_;

public:
    LotInspectionDossier(
        std::string_view lot,
        std::string_view pn,
        std::string_view mfg,
        uint32_t lot_sz,
        uint32_t sample_sz
    ) : lot_number_(lot), part_number_(pn), manufacturer_(mfg),
        lot_size_(lot_sz), sample_size_(sample_sz) {}

    void addRecord(SampleTestRecord rec) {
        records_.push_back(std::move(rec));
    }

    [[nodiscard]] size_t failedSamplesCount() const noexcept {
        return std::count_if(records_.begin(), records_.end(), [](const auto& r) {
            return r.defect != CounterfeitDefectType::None;
        });
    }

    [[nodiscard]] float calculateRiskIndex() const noexcept {
        if (sample_size_ == 0) return 1.0f;

        float weighted_score = 0.0f;
        for (const auto& r : records_) {
            switch (r.defect) {
                case CounterfeitDefectType::DecapWrongMaskId:
                case CounterfeitDefectType::DecapDieLogoAbsent:
                    weighted_score += 1.0f;
                    break;
                case CounterfeitDefectType::BlacktoppingDetected:
                case CounterfeitDefectType::SolventMarkRemoved:
                case CounterfeitDefectType::XrayDieSizeMismatch:
                    weighted_score += 0.8f;
                    break;
                case CounterfeitDefectType::AsaSignatureFailed:
                case CounterfeitDefectType::XrfLeadRohsViolation:
                    weighted_score += 0.6f;
                    break;
                case CounterfeitDefectType::QuiescentCurrentHigh:
                case CounterfeitDefectType::Pin1IndentModified:
                    weighted_score += 0.4f;
                    break;
                default:
                    break;
            }
        }

        return std::min(1.0f, weighted_score / static_cast<float>(sample_size_));
    }

    [[nodiscard]] LotDisposition evaluateDisposition() const noexcept {
        if (calculateRiskIndex() > 0.15f || failedSamplesCount() > 0) {
            return LotDisposition::QuarantineReject;
        }
        return LotDisposition::Accept;
    }

    void printReport() const {
        std::cout << "====================================================================\n";
        std::cout << " ПРОТОКОЛ ВХІДНОГО КОНТРОЛЮ КОМПОНЕНТІВ (AS6081 / IDEA-STD-1010)   \n";
        std::cout << "====================================================================\n";
        std::cout << " Партномер:       " << part_number_ << "\n";
        std::cout << " Виробник (OCM):  " << manufacturer_ << "\n";
        std::cout << " Номер партії:    " << lot_number_ << "\n";
        std::cout << " Обсяг партії:    " << lot_size_ << " шт. (Вибірка: " << sample_size_ << " шт.)\n";
        std::cout << " Забраковано:     " << failedSamplesCount() << " зразків\n";
        std::cout << " Індекс ризику:   " << std::fixed << std::setprecision(2) << calculateRiskIndex() << " / 1.00\n";

        auto disp = evaluateDisposition();
        std::cout << " ВЕРДИКТ ПАРТІЇ:  "
                  << (disp == LotDisposition::Accept ? "[✓ ПРИДАТНО ДО ВИРОБНИЦТВА]" :
                      disp == LotDisposition::SuspectHold ? "[? ПРИЗУПИНЕНО / ПОВТОРНИЙ ТЕСТ]" :
                      "[✗ КАРАНТИН / КОНТРАФАКТ]") << "\n";
        std::cout << "--------------------------------------------------------------------\n";
        std::cout << " Зразок | Рівень | Тип дефекту                  | Метрика | Примітка\n";
        std::cout << "--------+--------+------------------------------+---------+---------\n";

        for (const auto& r : records_) {
            std::string_view def_name = "БЕЗ ДЕФЕКТІВ";
            switch (r.defect) {
                case CounterfeitDefectType::BlacktoppingDetected:  def_name = "Blacktopping (епоксид)"; break;
                case CounterfeitDefectType::SolventMarkRemoved:   def_name = "Маркування змите ацетоном"; break;
                case CounterfeitDefectType::Pin1IndentModified:   def_name = "Фрезерована мітка Pin 1"; break;
                case CounterfeitDefectType::XrayDieSizeMismatch: def_name = "Розмір кристала X-Ray"; break;
                case CounterfeitDefectType::XrayBondWireDefect:  def_name = "Дефект розварки дротів"; break;
                case CounterfeitDefectType::XrfLeadRohsViolation:def_name = "Невідповідність RoHS XRF"; break;
                case CounterfeitDefectType::DecapDieLogoAbsent:  def_name = "Відсутній логотип кристала"; break;
                case CounterfeitDefectType::DecapWrongMaskId:    def_name = "Чужий Mask ID кристала"; break;
                case CounterfeitDefectType::AsaSignatureFailed:   def_name = "Збій сигнатури Curve Tracer"; break;
                case CounterfeitDefectType::QuiescentCurrentHigh: def_name = "Струм спокою IDD_q > Max"; break;
                default: break;
            }

            std::cout << " #" << std::setw(5) << std::left << r.sample_id << " | "
                      << "Рівень " << static_cast<int>(r.level) << " | "
                      << std::setw(28) << std::left << def_name << " |  "
                      << std::setw(5) << std::right << std::fixed << std::setprecision(1) << r.measured_metric << "  | "
                      << r.notes << "\n";
        }
        std::cout << "====================================================================\n";
    }
};

} // namespace SysNotary::CounterfeitMitigation

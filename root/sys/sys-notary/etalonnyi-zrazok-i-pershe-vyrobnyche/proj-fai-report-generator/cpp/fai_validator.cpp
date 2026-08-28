// =========================================================================
// fai_validator.cpp - Мова C++ (C++20)
// Ідіоматичний валідатор звітів першої виробничої партії (AS9102 Form 3)
// =========================================================================

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <cmath>
#include <format>
#include <algorithm>
#include <numeric>
#include <expected>

namespace fai {

enum class ParamType {
    AnalogTwoSided,
    UpperBoundOnly,
    DigitalHash
};

enum class Verdict {
    Pass,
    WarningLowCpk,
    FailOutOfSpec,
    FailHashMismatch
};

struct SpecItem {
    std::string name;
    std::string unit;
    ParamType type;
    double golden_nominal{0.0};
    double lsl{0.0};
    double usl{0.0};
    std::string golden_hash{};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        if (type == ParamType::AnalogTwoSided) return usl > lsl;
        if (type == ParamType::UpperBoundOnly) return usl > golden_nominal;
        return !golden_hash.empty();
    }
};

struct BoardRecord {
    std::string serial_number;
    std::vector<double> analog_measurements;
    std::vector<std::string> hash_measurements;
};

struct ParameterAnalysis {
    double mean{0.0};
    double std_dev{0.0};
    double cp{0.0};
    double cpu{0.0};
    double cpl{0.0};
    double cpk{0.0};
    double golden_drift{0.0};
    size_t out_of_spec_count{0};
    size_t outlier_count{0};
    Verdict verdict{Verdict::Pass};
};

struct BatchSummary {
    size_t total_boards{0};
    size_t total_params{0};
    size_t passed_params{0};
    size_t warning_params{0};
    size_t failed_params{0};
    bool overall_pass{true};
};

class Validator {
public:
    [[nodiscard]] static ParameterAnalysis analyze(const SpecItem& spec,
                                                   std::span<const BoardRecord> boards,
                                                   size_t param_idx) noexcept {
        ParameterAnalysis res{};

        if (spec.type == ParamType::DigitalHash) {
            for (const auto& b : boards) {
                if (param_idx < b.hash_measurements.size()) {
                    if (b.hash_measurements[param_idx] != spec.golden_hash) {
                        res.out_of_spec_count++;
                        res.verdict = Verdict::FailHashMismatch;
                    }
                } else {
                    res.out_of_spec_count++;
                    res.verdict = Verdict::FailHashMismatch;
                }
            }
            return res;
        }

        // Онлайн-накопичення статистики за алгоритмом Велфорда
        double mean = 0.0;
        double m2 = 0.0;
        size_t count = 0;

        for (const auto& b : boards) {
            if (param_idx >= b.analog_measurements.size()) continue;
            double val = b.analog_measurements[param_idx];
            ++count;
            double delta = val - mean;
            mean += delta / static_cast<double>(count);
            double delta2 = val - mean;
            m2 += delta * delta2;

            if (spec.type == ParamType::AnalogTwoSided) {
                if (val < spec.lsl || val > spec.usl) {
                    res.out_of_spec_count++;
                }
            } else if (spec.type == ParamType::UpperBoundOnly) {
                if (val > spec.usl) {
                    res.out_of_spec_count++;
                }
            }
        }

        double variance = (count > 1) ? (m2 / static_cast<double>(count - 1)) : 0.0;
        double std_dev = std::sqrt(variance);
        if (std_dev < 1e-9) {
            std_dev = 1e-9;
        }

        res.mean = mean;
        res.std_dev = std_dev;
        res.golden_drift = mean - spec.golden_nominal;

        // Пошук викидів за Z-критерієм
        for (const auto& b : boards) {
            if (param_idx >= b.analog_measurements.size()) continue;
            double val = b.analog_measurements[param_idx];
            double z = std::abs(val - mean) / std_dev;
            if (z > 3.5) {
                res.outlier_count++;
            }
        }

        // Обчислення індексів придатності процесу
        if (spec.type == ParamType::AnalogTwoSided) {
            double spec_width = spec.usl - spec.lsl;
            res.cp = spec_width / (6.0 * std_dev);
            res.cpu = (spec.usl - mean) / (3.0 * std_dev);
            res.cpl = (mean - spec.lsl) / (3.0 * std_dev);
            res.cpk = std::min(res.cpu, res.cpl);
        } else if (spec.type == ParamType::UpperBoundOnly) {
            res.cp = (spec.usl - spec.golden_nominal) / (3.0 * std_dev);
            res.cpu = (spec.usl - mean) / (3.0 * std_dev);
            res.cpl = 0.0;
            res.cpk = res.cpu;
        }

        if (res.out_of_spec_count > 0) {
            res.verdict = Verdict::FailOutOfSpec;
        } else if (res.cpk < 1.33) {
            res.verdict = Verdict::WarningLowCpk;
        } else {
            res.verdict = Verdict::Pass;
        }

        return res;
    }

    static BatchSummary generate_report(std::span<const SpecItem> specs,
                                        std::span<const BoardRecord> boards) {
        BatchSummary summary{
            .total_boards = boards.size(),
            .total_params = specs.size(),
            .passed_params = 0,
            .warning_params = 0,
            .failed_params = 0,
            .overall_pass = true
        };

        std::cout << "==================================================================================================\n";
        std::cout << "                    ПРОТОКОЛ ВАЛІДАЦІЇ ПЕРШОЇ ВИРОБНИЧОЇ ПАРТІЇ (AS9102 FORM 3)                  \n";
        std::cout << "==================================================================================================\n";
        std::cout << std::format("Розмір вибірки: N = {} плат | Кількість контрольованих параметрів: {}\n\n",
                                 boards.size(), specs.size());

        std::cout << std::format("{:<22} | {:<6} | {:<8} | {:<16} | {:<8} | {:<6} | {:<6} | {:<14}\n",
                                 "Параметр", "Один.", "Еталон", "Поле допуску", "Факт (μ)", "σ", "Cpk", "Вердикт");
        std::cout << "--------------------------------------------------------------------------------------------------\n";

        for (size_t p = 0; p < specs.size(); ++p) {
            const auto& spec = specs[p];
            auto analysis = analyze(spec, boards, p);

            std::string spec_range;
            std::string nominal_str;
            std::string mean_str;
            std::string std_str;
            std::string cpk_str;
            std::string verdict_str;

            if (spec.type == ParamType::DigitalHash) {
                spec_range = "Exact Match";
                nominal_str = "SHA-256";
                mean_str = "MATCH";
                std_str = "N/A";
                cpk_str = "N/A";
            } else {
                if (spec.type == ParamType::AnalogTwoSided) {
                    spec_range = std::format("[{:.3f}..{:.3f}]", spec.lsl, spec.usl);
                } else {
                    spec_range = std::format("[ <= {:.3f} ]", spec.usl);
                }
                nominal_str = std::format("{:.3f}", spec.golden_nominal);
                mean_str = std::format("{:.3f}", analysis.mean);
                std_str = std::format("{:.4f}", analysis.std_dev);
                cpk_str = std::format("{:.2f}", analysis.cpk);
            }

            switch (analysis.verdict) {
                case Verdict::Pass:
                    verdict_str = "[ PASS ]";
                    summary.passed_params++;
                    break;
                case Verdict::WarningLowCpk:
                    verdict_str = "[!CPK < 1.33!]";
                    summary.warning_params++;
                    break;
                case Verdict::FailOutOfSpec:
                    verdict_str = "[*FAIL OOS*]";
                    summary.failed_params++;
                    summary.overall_pass = false;
                    break;
                case Verdict::FailHashMismatch:
                    verdict_str = "[*FAIL HASH*]";
                    summary.failed_params++;
                    summary.overall_pass = false;
                    break;
            }

            std::cout << std::format("{:<22} | {:<6} | {:<8} | {:<16} | {:<8} | {:<6} | {:<6} | {:<14}\n",
                                     spec.name, spec.unit, nominal_str, spec_range,
                                     mean_str, std_str, cpk_str, verdict_str);
        }

        std::cout << "==================================================================================================\n";
        std::cout << std::format("ПІДСУМОК: Успішно: {} | Попередження Cpk: {} | Критичних дефектів: {}\n",
                                 summary.passed_params, summary.warning_params, summary.failed_params);
        
        std::string final_status = summary.overall_pass ? 
            (summary.warning_params > 0 ? "УМОВНО СХВАЛЕНО (Потрібен контроль Cpk)" : 
                                          "ПОВНІСТЮ СХВАЛЕНО ДЛЯ СЕРІЙНОГО ВИПУСКУ") :
            "ВІДХИЛЕНО — ПАРТІЯ ЗАБЛОКОВАНА ДЛЯ ВІДВАНТАЖЕННЯ";
        std::cout << std::format("ФІНАЛЬНИЙ СТАТУС ПАРТІЇ: {}\n", final_status);
        std::cout << "==================================================================================================\n\n";

        return summary;
    }
};

} // namespace fai

int main() {
    std::vector<fai::SpecItem> specs = {
        {
            .name = "VCC_3V3 (Main Rail)",
            .unit = "V",
            .type = fai::ParamType::AnalogTwoSided,
            .golden_nominal = 3.300,
            .lsl = 3.135,
            .usl = 3.465
        },
        {
            .name = "VCC_1V1 (Core Rail)",
            .unit = "V",
            .type = fai::ParamType::AnalogTwoSided,
            .golden_nominal = 1.100,
            .lsl = 1.045,
            .usl = 1.155
        },
        {
            .name = "RTC_CLK (Frequency)",
            .unit = "kHz",
            .type = fai::ParamType::AnalogTwoSided,
            .golden_nominal = 32.768,
            .lsl = 32.760,
            .usl = 32.776
        },
        {
            .name = "BGA_MCU_Voiding",
            .unit = "%",
            .type = fai::ParamType::UpperBoundOnly,
            .golden_nominal = 5.0,
            .lsl = 0.0,
            .usl = 15.0
        },
        {
            .name = "FW_SHA256_Hash",
            .unit = "HEX",
            .type = fai::ParamType::DigitalHash,
            .golden_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
    };

    std::vector<fai::BoardRecord> sample_boards(10);
    std::vector<double> vcc3v3 = {3.310, 3.305, 3.315, 3.302, 3.308, 3.312, 3.304, 3.309, 3.311, 3.306};
    std::vector<double> vcc1v1 = {1.102, 1.098, 1.101, 1.099, 1.103, 1.100, 1.097, 1.102, 1.101, 1.099};
    std::vector<double> rtc    = {32.768, 32.769, 32.767, 32.768, 32.769, 32.768, 32.767, 32.768, 32.769, 32.768};
    std::vector<double> voids  = {6.2, 7.1, 5.8, 8.4, 6.9, 7.5, 5.2, 6.8, 7.9, 6.4};

    for (size_t i = 0; i < 10; ++i) {
        sample_boards[i].serial_number = std::format("SN-2026-FA-{:04d}", i + 1);
        sample_boards[i].analog_measurements = {vcc3v3[i], vcc1v1[i], rtc[i], voids[i]};
        sample_boards[i].hash_measurements = {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        };
    }

    auto summary = fai::Validator::generate_report(specs, sample_boards);
    return summary.overall_pass ? 0 : 1;
}

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <cmath>
#include <cstdint>
#include <algorithm>
#include <iomanip>

namespace eol::sanitizer {

enum class Severity {
    Info,
    Warning,
    Critical
};

enum class FindingType {
    BinaryMagic,
    HighEntropy,
    NdaMarker,
    PrivateKey
};

struct Finding {
    FindingType type;
    Severity severity;
    std::string_view rule_name;
    std::string description;
    std::size_t offset;
};

struct ScanReport {
    std::size_t file_size{0};
    double entropy{0.0};
    std::vector<Finding> findings;

    [[nodiscard]] bool has_critical_findings() const noexcept {
        return std::any_of(findings.begin(), findings.end(), [](const Finding& f) {
            return f.severity == Severity::Critical;
        });
    }
};

struct BinarySignature {
    std::span<const uint8_t> magic;
    std::string_view format_name;
};

class RepositorySanitizer {
public:
    static constexpr double ENTROPY_THRESHOLD = 7.2;
    static constexpr std::size_t MIN_BUFFER_FOR_ENTROPY = 256;

    static double calculate_shannon_entropy(std::span<const uint8_t> data) noexcept {
        if (data.empty()) return 0.0;

        std::array<std::size_t, 256> byte_counts{};
        for (uint8_t byte : data) {
            byte_counts[byte]++;
        }

        double entropy = 0.0;
        const double total = static_cast<double>(data.size());
        for (std::size_t count : byte_counts) {
            if (count > 0) {
                const double p = static_cast<double>(count) / total;
                entropy -= p * (std::log(p) / std::log(2.0));
            }
        }
        return entropy;
    }

    [[nodiscard]] ScanReport scan(std::span<const uint8_t> buffer) const {
        ScanReport report;
        report.file_size = buffer.size();
        report.entropy = calculate_shannon_entropy(buffer);

        check_binary_signatures(buffer, report);
        check_entropy_anomaly(buffer, report);
        check_text_patterns(buffer, report);

        return report;
    }

private:
    static void check_binary_signatures(std::span<const uint8_t> buffer, ScanReport& report) {
        static constexpr uint8_t ELF_M[] = {0x7F, 'E', 'L', 'F'};
        static constexpr uint8_t PE_M[]  = {'M', 'Z'};
        static constexpr uint8_t JAVA_M[]= {0xCA, 0xFE, 0xBA, 0xBE};
        static constexpr uint8_t UIMG_M[]= {0x27, 0x05, 0x19, 0x56};
        static constexpr uint8_t DTB_M[] = {0xD0, 0x0D, 0xFE, 0xED};

        static const std::array<BinarySignature, 5> signatures = {{
            {ELF_M, "Executable and Linkable Format (ELF)"},
            {PE_M, "DOS/PE Executable (MZ)"},
            {JAVA_M, "Mach-O / Java Class (Fat Binary)"},
            {UIMG_M, "U-Boot Legacy Image (uImage)"},
            {DTB_M, "Flattened Device Tree (DTB)"}
        }};

        for (const auto& sig : signatures) {
            if (buffer.size() >= sig.magic.size() &&
                std::equal(sig.magic.begin(), sig.magic.end(), buffer.begin())) {
                report.findings.push_back(Finding{
                    FindingType::BinaryMagic,
                    Severity::Critical,
                    "BIN_HEADER",
                    std::string(sig.format_name),
                    0
                });
            }
        }
    }

    static void check_entropy_anomaly(std::span<const uint8_t> buffer, ScanReport& report) {
        if (buffer.size() >= MIN_BUFFER_FOR_ENTROPY && report.entropy >= ENTROPY_THRESHOLD) {
            report.findings.push_back(Finding{
                FindingType::HighEntropy,
                Severity::Warning,
                "HIGH_ENTROPY",
                "Висока ентропія (" + std::to_string(report.entropy).substr(0, 4) + " біт/байт): зашитий блоб",
                0
            });
        }
    }

    static void check_text_patterns(std::span<const uint8_t> buffer, ScanReport& report) {
        const std::string_view text(reinterpret_cast<const char*>(buffer.data()), buffer.size());

        static constexpr std::array<std::string_view, 5> nda_rules = {
            "CONFIDENTIAL AND PROPRIETARY",
            "DO NOT DISTRIBUTE",
            "QUALCOMM PROPRIETARY",
            "BROADCOM PROPRIETARY",
            "MEDIATEK STRICT NDA"
        };

        for (std::string_view rule : nda_rules) {
            const auto pos = text.find(rule);
            if (pos != std::string_view::npos) {
                report.findings.push_back(Finding{
                    FindingType::NdaMarker,
                    Severity::Critical,
                    "NDA_POLICY",
                    std::string(rule),
                    pos
                });
            }
        }

        static constexpr std::array<std::string_view, 3> key_rules = {
            "-----BEGIN RSA PRIVATE KEY-----",
            "-----BEGIN EC PRIVATE KEY-----",
            "-----BEGIN PRIVATE KEY-----"
        };

        for (std::string_view rule : key_rules) {
            const auto pos = text.find(rule);
            if (pos != std::string_view::npos) {
                report.findings.push_back(Finding{
                    FindingType::PrivateKey,
                    Severity::Critical,
                    "LEAKED_SECRET",
                    std::string(rule),
                    pos
                });
            }
        }
    }
};

void print_report(std::string_view filename, const ScanReport& report) {
    std::cout << "=================================================================\n";
    std::cout << "Звіт санітизації: " << filename << " (Розмір: " << report.file_size
              << " байт, Ентропія: " << std::fixed << std::setprecision(2) << report.entropy << " біт/байт)\n";
    std::cout << "=================================================================\n";

    if (report.findings.empty()) {
        std::cout << " [OK] Жодних закритих блобів або секретів не виявлено.\n\n";
        return;
    }

    for (const auto& f : report.findings) {
        const char* sev = (f.severity == Severity::Critical) ? "CRITICAL" :
                          (f.severity == Severity::Warning)  ? "WARNING" : "INFO";
        std::cout << " [" << std::left << std::setw(8) << sev << "] Правило: "
                  << std::setw(14) << f.rule_name << " | Зсув: 0x" << std::hex << std::setw(6)
                  << std::setfill('0') << f.offset << std::setfill(' ') << std::dec
                  << " | " << f.description << "\n";
    }
    std::cout << "-----------------------------------------------------------------\n";
    std::cout << " Загалом зауважень: " << report.findings.size() << "\n\n";
}

} // namespace eol::sanitizer

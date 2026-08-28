#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <expected>
#include <format>
#include <algorithm>
#include <numeric>
#include <cstdint>

namespace notary::lifecycle {

enum class CraClass : uint8_t {
    Default = 0,
    ImportantClassI,
    ImportantClassII,
    Critical
};

enum class Severity : uint8_t {
    Low = 0,
    Medium,
    High,
    Critical
};

enum class VexStatus : uint8_t {
    NotAffected = 0,
    Affected,
    Fixed,
    UnderInvestigation
};

struct HardwareRevision {
    std::string model_id;
    uint32_t hardware_rev_id;
    std::chrono::system_clock::time_point release_date;
    std::chrono::system_clock::time_point end_of_sale_date;
    std::chrono::system_clock::time_point promised_support_end;
    std::size_t flash_rom_capacity_bytes;
    std::size_t current_firmware_size_bytes;
    uint32_t security_version_number{1};
    CraClass cra_class;
};

struct VulnerabilityRecord {
    std::string cve_id;
    double cvss_score;
    double epss_probability;
    bool in_cisa_kev{false};
    bool is_zero_day_active{false};
    Severity severity;
    VexStatus vex_status;
    std::chrono::system_clock::time_point discovery_timestamp;

    [[nodiscard]] static constexpr Severity score_to_severity(double cvss) noexcept {
        if (cvss >= 9.0) return Severity::Critical;
        if (cvss >= 7.0) return Severity::High;
        if (cvss >= 4.0) return Severity::Medium;
        return Severity::Low;
    }
};

struct SbomComponent {
    std::string package_name;
    std::string purl;
    std::string version;
    std::size_t binary_size_bytes;
    std::vector<VulnerabilityRecord> vulnerabilities;
};

class ProductLifecycleManager {
public:
    explicit ProductLifecycleManager(HardwareRevision hw_rev)
        : hardware_(std::move(hw_rev)) {}

    void add_component(SbomComponent comp) {
        components_.push_back(std::move(comp));
    }

    [[nodiscard]] std::chrono::hours calculate_cra_notification_deadline(const VulnerabilityRecord& cve) const noexcept {
        if (cve.is_zero_day_active || cve.in_cisa_kev) {
            return std::chrono::hours{24}; // Early Warning to ENISA
        }
        if (cve.severity == Severity::Critical) {
            return std::chrono::hours{72}; // Mandatory Incident Notification
        }
        return std::chrono::hours{336}; // 14 days Final Assessment
    }

    [[nodiscard]] std::expected<double, std::string> evaluate_flash_headroom_after_patch(std::size_t patch_delta_bytes) const {
        std::size_t projected = hardware_.current_firmware_size_bytes + patch_delta_bytes;
        if (projected > hardware_.flash_rom_capacity_bytes) {
            return std::unexpected(std::format("Переповнення Flash: дельта {} перевищує ліміт на {} байтів",
                                               patch_delta_bytes, projected - hardware_.flash_rom_capacity_bytes));
        }
        std::size_t free_bytes = hardware_.flash_rom_capacity_bytes - projected;
        return (static_cast<double>(free_bytes) / static_cast<double>(hardware_.flash_rom_capacity_bytes)) * 100.0;
    }

    void print_full_audit_report(std::chrono::system_clock::time_point now) const {
        auto diff_support = std::chrono::duration_cast<std::chrono::hours>(hardware_.promised_support_end - now).count();
        double remaining_years = diff_support / (365.25 * 24.0);

        auto total_promised = std::chrono::duration_cast<std::chrono::hours>(hardware_.promised_support_end - hardware_.release_date).count();
        double total_years = total_promised / (365.25 * 24.0);

        std::cout << std::format("=== ЗВІТ АУДИТУ ПІДТРИМКИ: {} (REV {}) ===\n",
                                 hardware_.model_id, hardware_.hardware_rev_id);
        std::cout << std::format("Статус підтримки:      {} (Залишилося: {:.2f} років)\n",
                                 (remaining_years > 0.0 ? "АКТИВНА" : "ЗАКІНЧИЛАСЯ (EOL)"), remaining_years);
        std::cout << std::format("CRA 5-річний бенчмарк: {} (Всього обіцяно: {:.2f} років)\n",
                                 (total_years >= 5.0 ? "ВИКОНАНО" : "ПОРУШЕННЯ"), total_years);
        std::cout << std::format("Апаратний рівень SVN:  {}\n", hardware_.security_version_number);

        double current_free = (static_cast<double>(hardware_.flash_rom_capacity_bytes - hardware_.current_firmware_size_bytes) /
                               static_cast<double>(hardware_.flash_rom_capacity_bytes)) * 100.0;
        std::cout << std::format("Flash ROM статус:      {}/{} байтів ({:.1f}% вільно)\n\n",
                                 hardware_.current_firmware_size_bytes, hardware_.flash_rom_capacity_bytes, current_free);

        std::cout << "--- ТРІАЖ ВРАЗЛИВОСТЕЙ ТА ДЕДЛАЙНИ РЕГУЛЯТОРІВ ---\n";
        for (const auto& comp : components_) {
            for (const auto& cve : comp.vulnerabilities) {
                auto deadline = calculate_cra_notification_deadline(cve);
                std::string_view vex_str = (cve.vex_status == VexStatus::Affected) ? "AFFECTED" : "NOT_AFFECTED";
                std::cout << std::format("[{}] {} | Компонент: {}@{} | CVSS: {:.1f} | EPSS: {:.4f} | Сповіщення: <= {} год\n",
                                         cve.cve_id, vex_str, comp.package_name, comp.version,
                                         cve.cvss_score, cve.epss_probability, deadline.count());
            }
        }
    }

private:
    HardwareRevision hardware_;
    std::vector<SbomComponent> components_;
};

} // namespace notary::lifecycle

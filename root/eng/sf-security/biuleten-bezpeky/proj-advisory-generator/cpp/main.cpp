#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <sstream>

struct SemVer {
    int major = 0;
    int minor = 0;
    int patch = 0;

    auto operator<=>(const SemVer&) const = default;

    static std::optional<SemVer> parse(std::string_view str) {
        SemVer v;
        char dot1 = 0, dot2 = 0;
        std::stringstream ss{std::string(str)};
        if ((ss >> v.major >> dot1 >> v.minor >> dot2 >> v.patch) && dot1 == '.' && dot2 == '.') {
            return v;
        }
        return std::nullopt;
    }
};

enum class RemediationType {
    VendorFix,
    Workaround,
    Mitigation
};

struct Remediation {
    RemediationType type;
    std::string details;
    std::string fixed_version;
};

struct SecurityAdvisory {
    std::string cve_id;
    std::string cwe_id;
    double cvss_base_score = 0.0;
    std::string cvss_vector;
    SemVer min_affected;
    SemVer max_affected;
    Remediation remediation;

    [[nodiscard]] bool is_vulnerable(const SemVer& current) const noexcept {
        return (current >= min_affected && current <= max_affected);
    }
};

class AdvisoryEvaluator {
public:
    static void evaluate(const SecurityAdvisory& adv, std::string_view installed_ver_str) {
        const auto installed = SemVer::parse(installed_ver_str);
        if (!installed) {
            std::cerr << "Помилка: некоректний формат версії: " << installed_ver_str << "\n";
            return;
        }

        std::cout << "=== Аналіз бюлетеня: " << adv.cve_id << " ===\n";
        std::cout << "Клас дефекту: " << adv.cwe_id << " | CVSS: " << adv.cvss_base_score 
                  << " [" << adv.cvss_vector << "]\n";
        std::cout << "Перевірка версії: " << installed_ver_str << "\n";

        if (adv.is_vulnerable(*installed)) {
            std::cout << "[УВАГА] Система ВРАЗЛИВА! Встановлена версія підпадає під дію загрози.\n";
            if (adv.remediation.type == RemediationType::VendorFix) {
                std::cout << "Рекомендована дія: Оновити пакет до версії >= " << adv.remediation.fixed_version << "\n";
                std::cout << "Деталі: " << adv.remediation.details << "\n";
            } else if (adv.remediation.type == RemediationType::Workaround) {
                std::cout << "Рекомендована дія: Застосувати тимчасовий захід (Workaround)\n";
                std::cout << "Інструкція: " << adv.remediation.details << "\n";
            }
        } else {
            std::cout << "[OK] Встановлена версія безпечна (не зачеплена цією вадою).\n";
        }
        std::cout << "\n";
    }
};

int main() {
    const SecurityAdvisory adv{
        .cve_id = "CVE-2024-38856",
        .cwe_id = "CWE-787",
        .cvss_base_score = 9.8,
        .cvss_vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        .min_affected = SemVer{2, 1, 0},
        .max_affected = SemVer{2, 4, 3},
        .remediation = Remediation{
            .type = RemediationType::VendorFix,
            .details = "Встановіть оновлений пакет з репозиторію безпеки або вимкніть TLS-сесії.",
            .fixed_version = "2.4.4"
        }
    };

    AdvisoryEvaluator::evaluate(adv, "2.4.1");
    AdvisoryEvaluator::evaluate(adv, "2.4.4");
    AdvisoryEvaluator::evaluate(adv, "2.0.9");

    return 0;
}

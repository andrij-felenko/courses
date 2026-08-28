#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <format>
#include <span>

namespace audit {

enum class LicenseClass {
    Permissive,  // MIT, BSD, ISC
    Apache2,     // Apache 2.0
    Lgpl,        // LGPL v2.1/v3.0
    Gpl2,        // GPL-2.0-only
    Gpl3,        // GPL-3.0-or-later
    Proprietary  // Закритий комерційний код
};

enum class LinkType {
    Static,
    Dynamic,
    Ipc
};

struct ModuleDependency {
    std::string name;
    std::string spdx;
    LicenseClass license;
    LinkType linkage;
};

struct ComplianceViolation {
    std::string module_name;
    std::string spdx;
    std::string reason;
};

class LicenseEvaluator {
public:
    static constexpr bool is_compatible(LicenseClass target, LicenseClass dep, LinkType link) noexcept {
        if (link == LinkType::Ipc) {
            return true;
        }

        switch (target) {
        case LicenseClass::Proprietary:
            if (dep == LicenseClass::Permissive || dep == LicenseClass::Apache2) return true;
            if (dep == LicenseClass::Lgpl) return (link == LinkType::Dynamic);
            return false;

        case LicenseClass::Gpl2:
            if (dep == LicenseClass::Permissive || dep == LicenseClass::Gpl2) return true;
            if (dep == LicenseClass::Apache2 || dep == LicenseClass::Gpl3) return false;
            return true;

        case LicenseClass::Gpl3:
            if (dep == LicenseClass::Gpl2) return false;
            return true;

        default:
            return false;
        }
    }

    static std::expected<void, std::vector<ComplianceViolation>> verify_manifest(
        std::string_view target_name,
        LicenseClass target_lic,
        std::span<const ModuleDependency> dependencies)
    {
        std::vector<ComplianceViolation> errors;
        std::cout << std::format("=== АУДИТ ЛІЦЕНЗІЙНОЇ ВІДПОВІДНОСТІ: {} ===\n", target_name);

        for (const auto& dep : dependencies) {
            const bool valid = is_compatible(target_lic, dep.license, dep.linkage);
            const std::string_view link_str = (dep.linkage == LinkType::Static) ? "STATIC" :
                                              (dep.linkage == LinkType::Dynamic) ? "DYNAMIC" : "IPC";

            if (valid) {
                std::cout << std::format("[OK]   {:<15} ({:<10}) Link: {:<8}\n",
                                         dep.name, dep.spdx, link_str);
            } else {
                std::cout << std::format("[FAIL] {:<15} ({:<10}) Link: {:<8} <-- БЛОКУВАННЯ ЗБІРКИ!\n",
                                         dep.name, dep.spdx, link_str);
                errors.push_back({dep.name, dep.spdx, "Неприпустима комбінація ліцензії та лінкування"});
            }
        }

        std::cout << "----------------------------------------------------\n";
        if (!errors.empty()) {
            return std::unexpected(errors);
        }
        return {};
    }
};

} // namespace audit

int main() {
    using namespace audit;

    const std::vector<ModuleDependency> project_deps = {
        {"libjson-c",    "MIT",        LicenseClass::Permissive, LinkType::Static},
        {"libcrypto",    "Apache-2.0", LicenseClass::Apache2,    LinkType::Static},
        {"libprotocols", "LGPL-2.1",   LicenseClass::Lgpl,       LinkType::Dynamic},
        {"system-core",  "GPL-2.0",    LicenseClass::Gpl2,       LinkType::Ipc},
        {"libdsp_filter","GPL-2.0",    LicenseClass::Gpl2,       LinkType::Static} // Порушення!
    };

    auto result = LicenseEvaluator::verify_manifest("Firmware-App", LicenseClass::Proprietary, project_deps);

    if (!result) {
        std::cout << std::format("РЕЗУЛЬТАТ: Виявлено {} порушень. Збірку зупинено.\n", result.error().size());
        return 1;
    }

    std::cout << "РЕЗУЛЬТАТ: Всі залежності юридично сумісні.\n";
    return 0;
}

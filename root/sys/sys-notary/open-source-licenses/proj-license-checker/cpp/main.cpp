#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <format>
#include <span>

namespace license_audit {

enum class LicenseType {
    Unknown,
    Permissive,    // MIT, BSD, ISC
    Apache2,       // Apache 2.0
    WeakCopyleft,  // LGPL, MPL
    Gpl2Only,      // GPL-2.0-only
    Gpl3Plus,      // GPL-3.0+, LGPL-3.0+
    Agpl3,         // AGPL-3.0
    Proprietary    // Комерційні закриті умови
};

enum class Linkage {
    Static,
    Dynamic,
    IpcBoundary
};

struct Dependency {
    std::string name;
    std::string spdx_id;
    LicenseType type;
    Linkage linkage;
};

struct AuditViolation {
    std::string component_name;
    std::string spdx_id;
    std::string reason;
};

class ComplianceEngine {
public:
    static constexpr bool is_compatible(LicenseType target, LicenseType dep, Linkage link) noexcept {
        if (link == Linkage::IpcBoundary) {
            return true;
        }

        switch (target) {
        case LicenseType::Proprietary:
            if (dep == LicenseType::Permissive || dep == LicenseType::Apache2) {
                return true;
            }
            if (dep == LicenseType::WeakCopyleft) {
                return link == Linkage::Dynamic;
            }
            return false;

        case LicenseType::Gpl2Only:
            if (dep == LicenseType::Permissive || dep == LicenseType::Gpl2Only) {
                return true;
            }
            if (dep == LicenseType::Apache2 || dep == LicenseType::Gpl3Plus || dep == LicenseType::Agpl3) {
                return false; // Патентний конфлікт Apache 2.0 або невідповідність версій GPL
            }
            return true;

        case LicenseType::Gpl3Plus:
            if (dep == LicenseType::Permissive || dep == LicenseType::Apache2 ||
                dep == LicenseType::Gpl3Plus || dep == LicenseType::WeakCopyleft) {
                return true;
            }
            if (dep == LicenseType::Gpl2Only) {
                return false; // GPL-2.0-only без опції 'or-later' несумісна з v3
            }
            return true;

        default:
            return false;
        }
    }

    static std::expected<void, std::vector<AuditViolation>> audit(
        std::string_view project_name,
        LicenseType target_license,
        std::span<const Dependency> dependencies)
    {
        std::vector<AuditViolation> violations;
        std::cout << "[AUDIT C++] Перевірка проєкту: " << project_name << '\n';
        std::cout << "------------------------------------------------------------\n";

        for (const auto& dep : dependencies) {
            const bool compatible = is_compatible(target_license, dep.type, dep.linkage);
            const std::string_view link_str = (dep.linkage == Linkage::Static) ? "STATIC" :
                                              (dep.linkage == Linkage::Dynamic) ? "DYNAMIC (.so)" : "IPC";

            if (compatible) {
                std::cout << std::format("  [PASS] {:<15} | SPDX: {:<15} | Link: {:<12}\n",
                                         dep.name, dep.spdx_id, link_str);
            } else {
                std::cout << std::format("  [FAIL] {:<15} | SPDX: {:<15} | Link: {:<12}  <-- ЮРИДИЧНИЙ КОНФЛІКТ!\n",
                                         dep.name, dep.spdx_id, link_str);
                violations.push_back({
                    dep.name,
                    dep.spdx_id,
                    "Неприпустимий тип зв'язування або взаємна несумісність ліцензійних вимог"
                });
            }
        }

        std::cout << "------------------------------------------------------------\n";
        if (!violations.empty()) {
            return std::unexpected(violations);
        }
        return {};
    }
};

} // namespace license_audit

int main() {
    using namespace license_audit;

    const std::vector<Dependency> deps = {
        {"cJSON",       "MIT",                 LicenseType::Permissive,    Linkage::Static},
        {"mbedTLS",     "Apache-2.0",          LicenseType::Apache2,       Linkage::Static},
        {"libmodbus",   "LGPL-2.1-or-later",   LicenseType::WeakCopyleft,  Linkage::Dynamic},
        {"busybox",     "GPL-2.0-only",        LicenseType::Gpl2Only,      Linkage::IpcBoundary},
        {"libgpl_math", "GPL-2.0-only",        LicenseType::Gpl2Only,      Linkage::Static} // Порушення!
    };

    auto result = ComplianceEngine::audit("EdgeGateway-Daemon (Proprietary)", LicenseType::Proprietary, deps);

    if (!result) {
        std::cout << std::format("[ВИСНОВОК] Збірку заблоковано! Виявлено {} ліцензійних конфліктів.\n",
                                 result.error().size());
        return 1;
    }

    std::cout << "[ВИСНОВОК] Аудит пройдено успішно. Всі компоненти сумісні.\n";
    return 0;
}

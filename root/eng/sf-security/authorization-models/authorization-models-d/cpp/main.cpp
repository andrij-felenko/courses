#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <optional>
#include <expected>
#include <cstdint>
#include <span>

namespace authz {

enum class Permission : uint32_t {
    None   = 0,
    Read   = 1 << 0,
    Write  = 1 << 1,
    Delete = 1 << 2,
    Admin  = 1 << 3
};

constexpr Permission operator|(Permission a, Permission b) noexcept {
    return static_cast<Permission>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr Permission operator&(Permission a, Permission b) noexcept {
    return static_cast<Permission>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

enum class PolicyError {
    InvalidContext,
    EvaluationTimeout,
    BackendUnavailable
};

struct Subject {
    std::string user_id;
    std::vector<std::string> roles;
    std::string department;
    uint32_t clearance_level{0};
};

struct Resource {
    std::string resource_id;
    std::string department;
    uint32_t classification_level{0};
    std::string owner_id;
};

struct Environment {
    std::chrono::system_clock::time_point timestamp{std::chrono::system_clock::now()};
    bool is_corporate_network{true};
    uint32_t risk_score{0};
};

class PolicyDecisionPoint {
public:
    PolicyDecisionPoint() {
        role_definitions_["admin"]  = Permission::Read | Permission::Write | Permission::Delete | Permission::Admin;
        role_definitions_["editor"] = Permission::Read | Permission::Write;
        role_definitions_["viewer"] = Permission::Read;
    }

    [[nodiscard]] std::expected<bool, PolicyError> evaluate(
        const Subject& sub,
        const Resource& res,
        Permission action,
        const Environment& env
    ) const noexcept {
        // Fail-close: перевірка валідності вхідних даних
        if (sub.user_id.empty() || res.resource_id.empty()) {
            return std::unexpected(PolicyError::InvalidContext);
        }

        // 1. ABAC: Перевірка ризику та мережевого контексту
        if (env.risk_score > 80 || !env.is_corporate_network) {
            if ((action & (Permission::Write | Permission::Delete | Permission::Admin)) != Permission::None) {
                return false; // Відхилено через високий ризик
            }
        }

        // 2. MAC: Перевірка допуску суб'єкта проти грифа ресурсу
        if (sub.clearance_level < res.classification_level) {
            return false;
        }

        // 3. DAC: Прямий власник у своєму відділі має повні права
        if (sub.user_id == res.owner_id && sub.department == res.department) {
            return true;
        }

        // 4. RBAC: Агрегація прав за всіма ролями суб'єкта
        Permission granted_permissions = Permission::None;
        for (const auto& role : sub.roles) {
            if (auto it = role_definitions_.find(role); it != role_definitions_.end()) {
                granted_permissions = granted_permissions | it->second;
            }
        }

        // 5. ABAC: Дія дозволяється лише в межах того самого департаменту
        if (sub.department == res.department) {
            if ((granted_permissions & action) == action) {
                return true;
            }
        }

        // Суворе правило відмови за замовчанням (Deny by default)
        return false;
    }

private:
    std::unordered_map<std::string, Permission> role_definitions_;
};

class PolicyEnforcementPoint {
public:
    explicit PolicyEnforcementPoint(PolicyDecisionPoint pdp) : pdp_(std::move(pdp)) {}

    [[nodiscard]] bool authorize(
        const Subject& sub,
        const Resource& res,
        Permission action,
        const Environment& env
    ) {
        auto result = pdp_.evaluate(sub, res, action, env);

        bool allowed = false;
        if (result.has_value()) {
            allowed = result.value();
        } else {
            // При будь-якій помилці PDP обов'язково обираємо Fail-Close
            std::cerr << "[SECURITY ALERT] Authorization error encountered! Enforcing Fail-Close.\n";
            allowed = false;
        }

        log_audit(sub.user_id, res.resource_id, action, allowed);
        return allowed;
    }

private:
    void log_audit(std::string_view user, std::string_view resource, Permission act, bool verdict) const {
        std::cout << "[AUDIT C++20] User: " << user 
                  << " | Resource: " << resource 
                  << " | Action: " << static_cast<uint32_t>(act) 
                  << " | Verdict: " << (verdict ? "PERMIT" : "DENY") << "\n";
    }

    PolicyDecisionPoint pdp_;
};

} // namespace authz

int main() {
    using namespace authz;

    PolicyDecisionPoint pdp;
    PolicyEnforcementPoint pep(std::move(pdp));

    Subject alice{
        .user_id = "alice",
        .roles = {"editor"},
        .department = "engineering",
        .clearance_level = 4
    };

    Subject eve{
        .user_id = "eve",
        .roles = {"viewer"},
        .department = "marketing",
        .clearance_level = 1
    };

    Resource core_repo{
        .resource_id = "repo_core_engine",
        .department = "engineering",
        .classification_level = 3,
        .owner_id = "alice"
    };

    Environment safe_env{
        .timestamp = std::chrono::system_clock::now(),
        .is_corporate_network = true,
        .risk_score = 5
    };

    std::cout << "=== Демонстрація авторизації на C++20 ===\n\n";

    // Аліса редагує репозиторій інженерного відділу (Дозволено)
    pep.authorize(alice, core_repo, Permission::Write, safe_env);

    // Єва з маркетингу намагається видалити ядро (Відхилено)
    pep.authorize(eve, core_repo, Permission::Delete, safe_env);

    return 0;
}

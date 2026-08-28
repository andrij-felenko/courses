#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <chrono>
#include <algorithm>

enum class AuthDecision {
    Deny = 0,
    Allow = 1
};

enum class AuthReasonCode {
    DefaultDeny,
    ExplicitDeny,
    ExplicitAllow,
    ParseError,
    Timeout,
    InvalidContext
};

enum class RuleEffect {
    Deny,
    Allow
};

struct AccessRule {
    std::string subject_role;
    std::string action;
    std::string resource_prefix;
    RuleEffect effect;
    bool is_active{true};
};

struct AuthRequest {
    std::string subject_role;
    std::string action;
    std::string resource;
    std::chrono::system_clock::time_point timestamp{std::chrono::system_clock::now()};
};

struct AuthResult {
    AuthDecision decision{AuthDecision::Deny};
    AuthReasonCode reason{AuthReasonCode::DefaultDeny};
    std::optional<std::string> matched_rule{std::nullopt};

    [[nodiscard]] bool is_allowed() const noexcept {
        return decision == AuthDecision::Allow;
    }
};

class SafeAuthEngine {
public:
    explicit SafeAuthEngine(std::chrono::milliseconds timeout = std::chrono::milliseconds(50))
        : timeout_threshold_(timeout) {}

    void add_rule(AccessRule rule) {
        rules_.push_back(std::move(rule));
    }

    [[nodiscard]] AuthResult evaluate(const AuthRequest& req) const noexcept {
        // КРОК 1: Базовий стан - повна заборона
        AuthResult result{
            .decision = AuthDecision::Deny,
            .reason = AuthReasonCode::DefaultDeny,
            .matched_rule = std::nullopt
        };

        // Захисна валідація вхідних даних
        if (req.subject_role.empty() || req.action.empty() || req.resource.empty()) {
            result.reason = AuthReasonCode::ParseError;
            return result;
        }

        bool explicit_allow_matched = false;
        std::optional<std::string> allow_rule_id = std::nullopt;

        // КРОК 2: Оцінка правил із пріоритетом Explicit Deny
        for (const auto& rule : rules_) {
            if (!rule.is_active) continue;

            const bool role_match = (rule.subject_role == "*") || (rule.subject_role == req.subject_role);
            const bool action_match = (rule.action == "*") || (rule.action == req.action);
            const bool resource_match = req.resource.starts_with(rule.resource_prefix);

            if (role_match && action_match && resource_match) {
                if (rule.effect == RuleEffect::Deny) {
                    // Явна заборона негайно блокує запит
                    return AuthResult{
                        .decision = AuthDecision::Deny,
                        .reason = AuthReasonCode::ExplicitDeny,
                        .matched_rule = rule.resource_prefix
                    };
                }

                if (rule.effect == RuleEffect::Allow) {
                    explicit_allow_matched = true;
                    allow_rule_id = rule.resource_prefix;
                }
            }
        }

        // КРОК 3: Дозвіл лише за наявності явного збігу
        if (explicit_allow_matched) {
            result.decision = AuthDecision::Allow;
            result.reason = AuthReasonCode::ExplicitAllow;
            result.matched_rule = allow_rule_id;
        }

        return result;
    }

private:
    std::vector<AccessRule> rules_;
    std::chrono::milliseconds timeout_threshold_;
};

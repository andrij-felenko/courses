#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <variant>
#include <functional>
#include <optional>
#include <format>

enum class FieldType {
    String,
    Int,
    Float
};

struct FieldRule {
    std::string key;
    FieldType type;
    bool required{true};
};

struct ContractInteraction {
    std::string state_description;
    std::string method;
    std::string path;
    int expected_status;
    std::vector<FieldRule> rules;
};

struct HttpRequest {
    std::string method;
    std::string path;
};

using JsonValue = std::variant<std::string, int, double>;

struct HttpResponse {
    int status_code{0};
    std::map<std::string, JsonValue> body_fields;
};

/* ── Модель та бізнес-логіка постачальника (Provider) ── */

struct UserRecord {
    int user_id;
    std::string username;
    double balance;
    bool active;
};

class AccountProviderService {
public:
    void reset_to_state_user_42_active() {
        db_.clear();
        db_[42] = UserRecord{42, "andrij", 1250.75, true};
    }

    void reset_to_empty_state() {
        db_.clear();
    }

    [[nodiscard]] HttpResponse handle_request(const HttpRequest& req) const {
        if (req.method == "GET" && req.path.starts_with("/users/")) {
            try {
                int uid = std::stoi(req.path.substr(7));
                auto it = db_.find(uid);
                if (it != db_.end() && it->second.active) {
                    HttpResponse res;
                    res.status_code = 200;
                    res.body_fields["user_id"] = it->second.user_id;
                    res.body_fields["balance"] = it->second.balance;
                    // Додаткове поле, про яке клієнт не знає (Закон Постела)
                    res.body_fields["server_time"] = 1714567890;
                    return res;
                }
            } catch (...) {
                // Неправильний формат ідентифікатора
            }

            HttpResponse res;
            res.status_code = 404;
            res.body_fields["error_code"] = std::string("USER_NOT_FOUND");
            return res;
        }

        return HttpResponse{400, {}};
    }

private:
    std::map<int, UserRecord> db_;
};

/* ── Раннер верифікації контрактів ── */

class ContractVerificationHarness {
public:
    using StateCallback = std::function<void()>;

    void register_state(std::string state_name, StateCallback handler) {
        states_[std::move(state_name)] = std::move(handler);
    }

    [[nodiscard]] bool verify(const AccountProviderService& provider,
                              const std::vector<ContractInteraction>& contract) const {
        std::cout << "=== ЗАПУСК ВЕРИФІКАЦІЇ КОНТРАКТУ (C++20 HARNESS) ===\n";
        size_t passed = 0;

        for (const auto& interaction : contract) {
            std::cout << std::format("[RUN] Стан: '{}' -> {} {}\n",
                                     interaction.state_description, interaction.method, interaction.path);

            auto state_it = states_.find(interaction.state_description);
            if (state_it == states_.end()) {
                std::cout << std::format("  [FAIL] Не зареєстровано обробника для стану: '{}'\n",
                                         interaction.state_description);
                continue;
            }

            // 1. Встановлення стану
            state_it->second();

            // 2. Відтворення виклику
            HttpRequest req{interaction.method, interaction.path};
            HttpResponse res = provider.handle_request(req);

            // 3. Звірка статус-коду
            if (res.status_code != interaction.expected_status) {
                std::cout << std::format("  [FAIL] Статус-код: очікували {}, отримали {}\n",
                                         interaction.expected_status, res.status_code);
                continue;
            }

            // 4. Звірка полів за контрактом
            bool interaction_valid = true;
            for (const auto& rule : interaction.rules) {
                auto field_it = res.body_fields.find(rule.key);
                if (field_it == res.body_fields.end()) {
                    if (rule.required) {
                        std::cout << std::format("  [FAIL] Обов'язкове поле '{}' відсутнє!\n", rule.key);
                        interaction_valid = false;
                    }
                    continue;
                }

                bool type_matched = false;
                if (rule.type == FieldType::String && std::holds_alternative<std::string>(field_it->second)) {
                    type_matched = true;
                } else if (rule.type == FieldType::Int && std::holds_alternative<int>(field_it->second)) {
                    type_matched = true;
                } else if (rule.type == FieldType::Float && (std::holds_alternative<double>(field_it->second) ||
                                                             std::holds_alternative<int>(field_it->second))) {
                    type_matched = true;
                }

                if (!type_matched) {
                    std::cout << std::format("  [FAIL] Поле '{}': тип значення не відповідає правилу контракту\n", rule.key);
                    interaction_valid = false;
                }
            }

            if (interaction_valid) {
                std::cout << std::format("  [OK] Контракт виконано (статус {}, правил: {})\n",
                                         res.status_code, interaction.rules.size());
                passed++;
            }
        }

        std::cout << std::format("Підсумок: {} з {} взаємодій успішно верифіковано.\n", passed, contract.size());
        return passed == contract.size();
    }

private:
    std::map<std::string, StateCallback> states_;
};

int main() {
    AccountProviderService service;
    ContractVerificationHarness harness;

    // Реєстрація станів постачальника
    harness.register_state("user 42 exists and is active", [&]() {
        service.reset_to_state_user_42_active();
    });

    harness.register_state("no users exist in database", [&]() {
        service.reset_to_empty_state();
    });

    // Оголошення контракту споживача
    std::vector<ContractInteraction> contract = {
        {
            .state_description = "user 42 exists and is active",
            .method = "GET",
            .path = "/users/42",
            .expected_status = 200,
            .rules = {
                FieldRule{"user_id", FieldType::Int, true},
                FieldRule{"balance", FieldType::Float, true}
            }
        },
        {
            .state_description = "no users exist in database",
            .method = "GET",
            .path = "/users/999",
            .expected_status = 404,
            .rules = {
                FieldRule{"error_code", FieldType::String, true}
            }
        }
    };

    bool success = harness.verify(service, contract);
    return success ? 0 : 1;
}

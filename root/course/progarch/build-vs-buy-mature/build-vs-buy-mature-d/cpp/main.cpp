#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <expected>

// Доменна сутність користувача
struct UserIdentity {
    std::string user_id;
    std::string email;
    bool is_authenticated;
};

// 1. ПОРТ (Інтерфейс) — живе всередині нашого домену
class IAuthPort {
public:
    virtual ~IAuthPort() = default;
    virtual std::expected<UserIdentity, std::string> authenticate(
        std::string_view token) = 0;
};

// 2. АДАПТЕР A: SaaS Auth0
class Auth0Adapter final : public IAuthPort {
public:
    std::expected<UserIdentity, std::string> authenticate(
        std::string_view token) override 
    {
        // Виклики зовнішнього Auth0 API / SDK
        if (token.empty()) return std::unexpected("Auth0: invalid token");
        return UserIdentity{"auth0|12345", "user@example.com", true};
    }
};

// 3. АДАПТЕР B: Self-Hosted Keycloak (Репатріація!)
class KeycloakAdapter final : public IAuthPort {
public:
    std::expected<UserIdentity, std::string> authenticate(
        std::string_view token) override 
    {
        // Перевірка JWT підпису через локальний Keycloak JWKS
        if (token.empty()) return std::unexpected("Keycloak: invalid token");
        return UserIdentity{"kc-8899", "user@example.com", true};
    }
};

// Фабрика підміни адаптера через конфіг без зміни бізнес-коду
std::unique_ptr<IAuthPort> create_auth_provider(std::string_view provider_type) {
    if (provider_type == "saas_auth0") {
        return std::make_unique<Auth0Adapter>();
    }
    return std::make_unique<KeycloakAdapter>();
}

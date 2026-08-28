// cpp_deprecation.hpp — Застарівання для C++14/C++17/C++20
#pragma once

#include <string>
#include <string_view>
#include <optional>
#include <cstdint>

struct UserOptions {
    std::string_view user_id;
    std::string_view tenant_id{"tenant_default"};
    uint32_t flags{0};
};

class [[deprecated("UserStore v1 is deprecated. Migrate to TenantUserStore.")]] LegacyUserStore {
public:
    // Застарілий метод з обов'язковим текстовим поясненням і версією видалення
    [[deprecated("Use find_user(UserOptions const&) instead. Removal scheduled for v3.0.0.")]]
    std::optional<std::string> get_user_by_id(std::string_view id);

    // Новий метод розширеного контракту
    std::optional<std::string> find_user(UserOptions const& options);
};

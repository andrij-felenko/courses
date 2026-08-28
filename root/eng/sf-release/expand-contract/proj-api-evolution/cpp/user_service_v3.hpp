// user_service_v3.hpp — Фаза 3: Чистий контракт v3.0
#pragma once

#include <string>
#include <string_view>
#include <expected>
#include <cstdint>

struct UserLookupRequest {
    std::string_view user_id;
    std::string_view tenant_id;
    uint32_t flags{0};
};

struct UserProfile {
    std::string name;
    std::string email;
    bool is_active{true};
};

enum class ServiceError {
    InvalidArgument,
    UserNotFound,
    TenantNotFound,
    InternalStorageError
};

class UserService {
public:
    // Старий метод get_user_by_id вилучено з кодової бази.
    // Залишився лише чистий, оптимізований цільовий контракт:
    std::expected<UserProfile, ServiceError> find_user(UserLookupRequest const& req);
};

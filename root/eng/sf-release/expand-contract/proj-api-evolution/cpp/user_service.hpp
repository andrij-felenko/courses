// user_service.hpp — Фаза 1: Expand
#pragma once

#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <cstdint>

struct UserLookupRequest {
    std::string_view user_id;
    std::string_view tenant_id{"tenant_default"};
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
    // Старий інтерфейс: повертає результат через типізований std::expected
    std::expected<UserProfile, ServiceError> get_user_by_id(std::string_view user_id);

    // Новий розширений інтерфейс: повна багатоорендна модель
    std::expected<UserProfile, ServiceError> find_user(UserLookupRequest const& req);
};

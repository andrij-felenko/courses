// user_service.cpp — Реалізація Фази 1 (Expand)
#include "user_service.hpp"

std::expected<UserProfile, ServiceError> UserService::find_user(UserLookupRequest const& req) {
    if (req.user_id.empty()) {
        return std::unexpected(ServiceError::InvalidArgument);
    }
    
    std::string_view const tenant = req.tenant_id.empty() ? "tenant_default" : req.tenant_id;

    // Імітація доступу до бази даних
    if (req.user_id == "usr_101") {
        return UserProfile{
            .name = "Тарас Шевченко",
            .email = "taras@example.ua",
            .is_active = true
        };
    }
    return std::unexpected(ServiceError::UserNotFound);
}

// Старий метод перенаправляє виклик у новий інтерфейс із замовчуваним контекстом
std::expected<UserProfile, ServiceError> UserService::get_user_by_id(std::string_view user_id) {
    UserLookupRequest req{
        .user_id = user_id,
        .tenant_id = "tenant_default",
        .flags = 0
    };
    return find_user(req);
}

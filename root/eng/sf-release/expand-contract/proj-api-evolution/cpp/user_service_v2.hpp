// user_service_v2.hpp — Фаза 2: Застарівання та телеметрія
#pragma once
#include "user_service.hpp"
#include <atomic>

class UserServiceV2 {
private:
    inline static std::atomic<uint64_t> s_legacy_calls{0};
    inline static std::atomic<uint64_t> s_v2_calls{0};

public:
    [[deprecated("get_user_by_id is deprecated. Use find_user(UserLookupRequest) instead. Removal in v3.0.")]]
    std::expected<UserProfile, ServiceError> get_user_by_id(std::string_view user_id) {
        s_legacy_calls.fetch_add(1, std::memory_order_relaxed);
        UserLookupRequest req{.user_id = user_id, .tenant_id = "tenant_default", .flags = 0};
        return find_user(req);
    }

    std::expected<UserProfile, ServiceError> find_user(UserLookupRequest const& req) {
        s_v2_calls.fetch_add(1, std::memory_order_relaxed);
        if (req.user_id.empty()) {
            return std::unexpected(ServiceError::InvalidArgument);
        }
        if (req.user_id == "usr_101") {
            return UserProfile{.name = "Тарас Шевченко", .email = "taras@example.ua", .is_active = true};
        }
        return std::unexpected(ServiceError::UserNotFound);
    }

    static uint64_t legacy_call_count() noexcept {
        return s_legacy_calls.load(std::memory_order_relaxed);
    }

    static uint64_t v2_call_count() noexcept {
        return s_v2_calls.load(std::memory_order_relaxed);
    }
};

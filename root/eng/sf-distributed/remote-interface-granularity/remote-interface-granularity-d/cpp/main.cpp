#include <iostream>
#include <string>
#include <expected>
#include <chrono>
#include <span>
#include <vector>

struct UserProfile { std::string name; std::string email; };
struct UserAddress { std::string city; std::string street; };
struct UserDiscount { int discount_percent{0}; };
struct OrderSummary { int order_id{0}; int total_cents{0}; };

// Консолідований DTO
struct UserDashboardDTO {
    UserProfile profile;
    UserAddress address;
    UserDiscount discount;
    OrderSummary last_order;
};

enum class RpcError {
    NetworkTimeout,
    NotFound,
    SerializationError
};

class ChattyClient {
public:
    // 4 окремих виклики: клієнт платить повний RTT на кожному кроці
    static std::expected<UserDashboardDTO, RpcError> fetch_dashboard(int user_id) {
        auto profile = rpc_get_profile(user_id);
        if (!profile) return std::unexpected(profile.error());

        auto address = rpc_get_address(user_id);
        if (!address) return std::unexpected(address.error());

        auto discount = rpc_get_discount(user_id);
        if (!discount) return std::unexpected(discount.error());

        auto order = rpc_get_last_order(user_id);
        if (!order) return std::unexpected(order.error());

        return UserDashboardDTO{
            .profile = std::move(*profile),
            .address = std::move(*address),
            .discount = std::move(*discount),
            .last_order = std::move(*order)
        };
    }

private:
    static std::expected<UserProfile, RpcError> rpc_get_profile(int id) {
        if (id <= 0) return std::unexpected(RpcError::NotFound);
        return UserProfile{"Іван Петренко", "ivan@example.com"};
    }
    static std::expected<UserAddress, RpcError> rpc_get_address(int id) {
        if (id <= 0) return std::unexpected(RpcError::NotFound);
        return UserAddress{"Київ", "вул. Хрещатик, 1"};
    }
    static std::expected<UserDiscount, RpcError> rpc_get_discount(int id) {
        if (id <= 0) return std::unexpected(RpcError::NotFound);
        return UserDiscount{15};
    }
    static std::expected<OrderSummary, RpcError> rpc_get_last_order(int id) {
        if (id <= 0) return std::unexpected(RpcError::NotFound);
        return OrderSummary{10482, 45000};
    }
};

class ChunkyFacadeClient {
public:
    // 1 виклик: клієнт відправляє 1 запит і отримує повністю наповнений DTO
    static std::expected<UserDashboardDTO, RpcError> fetch_dashboard(int user_id) {
        if (user_id <= 0) return std::unexpected(RpcError::NotFound);

        // Сервер усередині свого процесу зв'язує доменні моделі без затримок
        return UserDashboardDTO{
            .profile = {"Іван Петренко", "ivan@example.com"},
            .address = {"Київ", "вул. Хрещатик, 1"},
            .discount = {15},
            .last_order = {10482, 45000}
        };
    }
};

// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <memory>

struct OrderPayloadV1 {
    std::string order_id;
    double amount;
};

enum class RestErrorCode {
    BadRequestMissingField,
    NetworkError,
    ServerError
};

class SyncBillingClient {
public:
    [[nodiscard]] std::expected<void, RestErrorCode> send_request(const OrderPayloadV1& payload) const {
        std::cout << "[REST Client C++] Sending V1 request: " << payload.order_id << "\n";
        
        // Сервер V2 вимагає tax_identifier
        bool server_requires_tax_id = true;
        if (server_requires_tax_id) {
            std::cout << "[REST Server V2] ERROR 400: Missing required 'tax_identifier'\n";
            return std::unexpected(RestErrorCode::BadRequestMissingField);
        }
        return {};
    }
};

int main() {
    SyncBillingClient client;
    OrderPayloadV1 order{"ORD-9901", 149.99};
    auto result = client.send_request(order);
    
    if (!result) {
        std::cout << "[System] Synchronous Lockstep Failure: Release is blocked!\n";
    }
    return 0;
}

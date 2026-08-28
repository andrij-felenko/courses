// C++20: Ідіоматичний вихідний шлюз з RAII, std::string_view та std::expected
#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <thread>
#include <chrono>
#include <format>

struct HttpResponse {
    int status_code{0};
    std::string body;
    bool is_network_error{false};
};

enum class GatewayError {
    NetworkTimeout,
    PayloadMismatch,
    FatalClientError,
    RetriesExhausted
};

class OutboundPaymentGateway {
public:
    explicit OutboundPaymentGateway(std::string api_url) : api_url_(std::move(api_url)) {}

    std::expected<HttpResponse, GatewayError> execute_charge(
        std::string_view order_id, double amount, int max_retries = 3
    ) {
        const std::string idempotency_key = std::format("charge_order_{}_v1", order_id);
        const std::string payload = std::format(R"({{"order_id":"{}","amount":{:.2f}}})", order_id, amount);

        std::chrono::seconds backoff{1};

        for (int attempt = 1; attempt <= max_retries; ++attempt) {
            std::cout << std::format("[OUTBOUND C++] Спроба {}/{} | Key: {}\n", attempt, max_retries, idempotency_key);
            
            auto res = mock_http_post(idempotency_key, payload, attempt);

            if (res.is_network_error || res.status_code >= 500) {
                std::cout << std::format("[WARN C++] Таймаут/5xx ({}). Пауза {}s\n", res.status_code, backoff.count());
                std::this_thread::sleep_for(backoff);
                backoff *= 2;
                continue;
            }

            if (res.status_code == 409) {
                std::cout << std::format("[WARN C++] 409 Conflict. Пауза {}s\n", backoff.count());
                std::this_thread::sleep_for(backoff);
                continue;
            }

            if (res.status_code == 200 || res.status_code == 201) {
                return res;
            }

            if (res.status_code == 422) {
                return std::unexpected(GatewayError::PayloadMismatch);
            }

            return std::unexpected(GatewayError::FatalClientError);
        }

        return std::unexpected(GatewayError::RetriesExhausted);
    }

private:
    std::string api_url_;

    HttpResponse mock_http_post(std::string_view key, std::string_view payload, int attempt) {
        if (attempt == 1) return HttpResponse{.status_code = 0, .body = "", .is_network_error = true};
        if (attempt == 2) return HttpResponse{.status_code = 409, .body = R"({"error":"in_flight"})"};
        return HttpResponse{.status_code = 200, .body = R"({"status":"charged","id":"ch_1092"})"};
    }
};

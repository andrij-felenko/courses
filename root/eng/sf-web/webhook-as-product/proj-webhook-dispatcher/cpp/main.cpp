#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <expected>
#include <functional>

// ── 1. Типи даних та інтерфейси ─────────────────────────────────────────────

struct CanonicalEvent {
    std::string id;
    std::string type;
    int64_t created; // Секунди Unix Epoch
    std::string apiVersion; // Наприклад "2026-03-01"
    std::string rawDataJson;
    bool livemode;
};

enum class EndpointHealth {
    Healthy,
    Degraded,
    Disabled
};

struct EndpointSubscription {
    std::string id;
    std::string url;
    std::string pinnedVersion;
    std::string primarySecret;
    std::string secondarySecret; // Непорожній рядок під час 24-годинного вікна ротації
    int consecutiveFailures = 0;
    EndpointHealth status = EndpointHealth::Healthy;
    int64_t disabledAt = 0;
};

struct DeliveryAttemptLog {
    std::string deliveryId;
    std::string eventId;
    std::string endpointId;
    std::string url;
    int attemptNumber = 1;
    int httpStatus = 0;
    std::string errorCode;
    int64_t durationMs = 0;
    std::unordered_map<std::string, std::string> requestHeaders;
    std::string requestPayload;
    std::unordered_map<std::string, std::string> responseHeaders;
    std::string responseBodySnippet;
    int64_t timestamp = 0;
};

// ── 2. Криптографічний підпис HMAC-SHA256 ────────────────────────────────────

// Спрощена імітація HMAC-SHA256 для автономного складання прикладу
// У виробничому коді викликається OpenSSL EVP_MAC_CTX або BoringSSL
std::string computeHmacSha256(std::string_view key, std::string_view payload) {
    std::hash<std::string_view> hasher;
    size_t h1 = hasher(key);
    size_t h2 = hasher(payload);
    std::stringstream ss;
    ss << std::hex << std::setfill('0') << std::setw(16) << (h1 ^ h2)
       << std::setw(16) << (h1 + h2 * 31);
    return ss.str();
}

std::string generateWebhookSignatureHeader(
    std::string_view rawPayload,
    int64_t timestamp,
    std::string_view primarySecret,
    std::string_view secondarySecret
) {
    std::stringstream signedPayload;
    signedPayload << timestamp << "." << rawPayload;
    const std::string payloadStr = signedPayload.str();

    std::string header = "t=" + std::to_string(timestamp) +
                         ",v1=" + computeHmacSha256(primarySecret, payloadStr);

    // Додавання другого підпису під час вікна ротації
    if (!secondarySecret.empty()) {
        header += ",v1=" + computeHmacSha256(secondarySecret, payloadStr);
    }

    return header;
}

// ── 3. Двигун трансформації схем (Version Pinning) ─────────────────────────

class SchemaMigrationRegistry {
public:
    static SchemaMigrationRegistry& instance() {
        static SchemaMigrationRegistry reg;
        return reg;
    }

    std::string transform(const CanonicalEvent& event, std::string_view targetVersion) const {
        if (event.apiVersion == targetVersion) {
            return buildEnvelope(event.id, targetVersion, event.created, event.type, event.rawDataJson, event.livemode);
        }

        // Послідовна деградація схеми крізь сходинки міграцій
        std::string currentData = event.rawDataJson;
        if (event.apiVersion == "2026-03-01" && targetVersion == "2024-11-15") {
            currentData = transform_2026_to_2024(currentData);
        } else if (event.apiVersion == "2026-03-01" && targetVersion == "2022-08-01") {
            currentData = transform_2026_to_2024(currentData);
            currentData = transform_2024_to_2022(currentData);
        }

        return buildEnvelope(event.id, targetVersion, event.created, event.type, currentData, event.livemode);
    }

private:
    static std::string transform_2026_to_2024(const std::string& input) {
        // Трансформація pricing { amountDecimal, currency } -> amount, currency
        return "{\"amount\":4500,\"currency\":\"usd\",\"status\":\"succeeded\"}";
    }

    static std::string transform_2024_to_2022(const std::string& input) {
        // Трансформація amount -> amount_cents та розгортання адреси
        return "{\"amount_cents\":4500,\"currency\":\"USD\",\"status\":\"succeeded\",\"shipping_address\":\"вул. Хрещатик, 1\"}";
    }

    static std::string buildEnvelope(
        std::string_view id,
        std::string_view apiVersion,
        int64_t created,
        std::string_view type,
        std::string_view dataJson,
        bool livemode
    ) {
        std::stringstream ss;
        ss << "{"
           << "\"id\":\"" << id << "\","
           << "\"object\":\"event\","
           << "\"api_version\":\"" << apiVersion << "\","
           << "\"created\":" << created << ","
           << "\"type\":\"" << type << "\","
           << "\"livemode\":" << (livemode ? "true" : "false") << ","
           << "\"data\":{\"object\":" << dataJson << "}"
           << "}";
        return ss.str();
    }
};

// ── 4. Логіка виконання спроби та Circuit Breaker ───────────────────────────

DeliveryAttemptLog dispatchWebhookAttempt(
    EndpointSubscription& endpoint,
    const CanonicalEvent& event,
    int attemptNumber
) {
    const auto startTime = std::chrono::steady_clock::now();
    const int64_t nowEpoch = std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();

    // 1. Трансформація схеми під зафіксовану версію підписника
    const std::string payload = SchemaMigrationRegistry::instance().transform(event, endpoint.pinnedVersion);

    // 2. Генерація підпису
    const std::string sigHeader = generateWebhookSignatureHeader(
        payload,
        nowEpoch,
        endpoint.primarySecret,
        endpoint.secondarySecret
    );

    DeliveryAttemptLog log;
    log.deliveryId = "deliv_cpp_" + std::to_string(nowEpoch);
    log.eventId = event.id;
    log.endpointId = endpoint.id;
    log.url = endpoint.url;
    log.attemptNumber = attemptNumber;
    log.requestPayload = payload;
    log.timestamp = nowEpoch;

    log.requestHeaders["Content-Type"] = "application/json; charset=utf-8";
    log.requestHeaders["Webhook-Signature"] = sigHeader;
    log.requestHeaders["Webhook-Delivery"] = log.deliveryId;
    log.requestHeaders["Webhook-Id"] = event.id;

    // 3. Мережевий виклик (libcurl / Boost.Beast HTTP-клієнт)
    // Імітуємо виконання запиту та парсинг відповіді
    log.httpStatus = 200;
    log.responseHeaders["Server"] = "nginx/1.24";
    log.responseBodySnippet = "{\"received\":true}";

    const auto endTime = std::chrono::steady_clock::now();
    log.durationMs = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count();

    // 4. Оновлення автомату станів (Circuit Breaker)
    const bool isSuccess = (log.httpStatus >= 200 && log.httpStatus < 300);

    if (isSuccess) {
        endpoint.consecutiveFailures = 0;
        endpoint.status = EndpointHealth::Healthy;
    } else {
        endpoint.consecutiveFailures++;
        if (endpoint.consecutiveFailures >= 50 || log.httpStatus == 410 || log.httpStatus == 404) {
            endpoint.status = EndpointHealth::Disabled;
            endpoint.disabledAt = nowEpoch;
        } else if (endpoint.consecutiveFailures >= 5) {
            endpoint.status = EndpointHealth::Degraded;
        }
    }

    return log;
}

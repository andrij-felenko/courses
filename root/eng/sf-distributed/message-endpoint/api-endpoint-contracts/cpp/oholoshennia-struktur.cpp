#include <string>
#include <optional>
#include <unordered_map>
#include <cstdint>

struct MessageHeaders {
    // Ідентифікатори та кореляція
    std::string id;                                     // UUIDv7
    std::optional<std::string> correlation_id;
    std::optional<std::string> causation_id;
    
    // Адресація та маршрутизація
    std::string partition_key;                          // Ключ сутності
    std::optional<std::string> reply_to;                // Адреса відповіді
    std::string destination;                            // Цільовий топік/черга
    
    // Метадані вмісту та часу
    std::string content_type = "application/json";
    int64_t timestamp_utc_ms = 0;
    int64_t expires_at_utc_ms = 0;                      // 0 = без обмеження
    uint16_t schema_version = 1;
    
    // Стан надійності
    uint32_t delivery_attempt = 1;
    bool redelivered = false;
    
    // Розподілене трасування W3C
    std::string traceparent;
    std::string tracestate;
    
    // Користувацькі додаткові атрибути
    std::unordered_map<std::string, std::string> custom_attributes;
};

template <typename TPayload>
struct Message {
    MessageHeaders headers;
    TPayload payload;
};

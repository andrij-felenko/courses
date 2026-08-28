#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <cstdint>
#include <chrono>
#include <expected>
#include <optional>
#include <sstream>
#include <iomanip>

namespace integration {

/* Канонічні статуси замовлення */
enum class OrderStatus : uint8_t {
    Created = 1,
    Confirmed = 2,
    Shipped = 3,
    Cancelled = 4
};

/* Коди помилок трансляції */
enum class TranslationError : uint8_t {
    SyntaxError,
    InvalidCurrency,
    InvalidStatus,
    InvalidAmount,
    BufferOverflow
};

/* Канонічна модель даних замовлення */
struct CanonicalOrderMessage {
    std::string message_id;
    std::string correlation_id;
    uint64_t timestamp_ms{0};
    uint32_t schema_version{1};

    uint64_t order_id{0};
    std::string customer_ref;
    uint64_t amount_cents{0};
    std::string currency;
    OrderStatus status{OrderStatus::Created};
};

/* Модель мертвої черги (DLQ) */
struct DeadLetterEnvelope {
    std::string dlq_id;
    TranslationError error_code;
    std::string error_reason;
    uint64_t failed_at_ms{0};
    std::string raw_payload;
};

class MessageTranslator {
public:
    static uint64_t current_time_millis() noexcept {
        const auto now = std::chrono::system_clock::now();
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()
        ).count();
    }

    static std::string generate_id(std::string_view prefix, uint64_t seed) {
        std::ostringstream ss;
        ss << prefix << "-" << std::hex << std::setfill('0')
           << std::setw(8) << (seed & 0xFFFFFFFF)
           << "-4000-8000-"
           << std::setw(12) << (seed ^ 0xDEADBEEFULL);
        return ss.str();
    }

    /* Головна точка входу: повертає канонічне повідомлення або DLQ-конверт */
    static std::expected<CanonicalOrderMessage, DeadLetterEnvelope> translate(
        std::string_view raw_input,
        std::string_view correlation_id
    ) {
        const uint64_t now_ms = current_time_millis();

        // 1. Розбір рядка за роздільником ';'
        std::vector<std::string_view> tokens;
        size_t start = 0;
        while (start < raw_input.size()) {
            const size_t end = raw_input.find(';', start);
            if (end == std::string_view::npos) {
                tokens.push_back(raw_input.substr(start));
                break;
            }
            tokens.push_back(raw_input.substr(start, end - start));
            start = end + 1;
        }

        if (tokens.size() != 5) {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::SyntaxError,
                .error_reason = "Invalid syntax: expected 5 tokens, got " + std::to_string(tokens.size()),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 2. Безпечне зчитування полів
        uint64_t order_id = 0;
        uint64_t cents = 0;
        int legacy_status = 0;

        try {
            order_id = std::stoull(std::string(tokens[0]));
            cents = std::stoull(std::string(tokens[2]));
            legacy_status = std::stoi(std::string(tokens[4]));
        } catch (const std::exception& e) {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::SyntaxError,
                .error_reason = std::string("Numeric parse failure: ") + e.what(),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 3. Семантична валідація суми
        if (cents == 0 || cents > 100'000'000'000ULL) {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::InvalidAmount,
                .error_reason = "Amount cents out of bounds: " + std::to_string(cents),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 4. Валідація коду валюти
        const std::string_view curr = tokens[3];
        if (curr != "UAH" && curr != "USD" && curr != "EUR") {
            return std::unexpected(DeadLetterEnvelope{
                .dlq_id = generate_id("dlq", now_ms),
                .error_code = TranslationError::InvalidCurrency,
                .error_reason = "Unsupported currency code: " + std::string(curr),
                .failed_at_ms = now_ms,
                .raw_payload = std::string(raw_input)
            });
        }

        // 5. Мапінг статусів
        OrderStatus status;
        switch (legacy_status) {
            case 101: status = OrderStatus::Created; break;
            case 102: status = OrderStatus::Confirmed; break;
            case 103: status = OrderStatus::Shipped; break;
            case 999: status = OrderStatus::Cancelled; break;
            default:
                return std::unexpected(DeadLetterEnvelope{
                    .dlq_id = generate_id("dlq", now_ms),
                    .error_code = TranslationError::InvalidStatus,
                    .error_reason = "Unknown legacy status code: " + std::to_string(legacy_status),
                    .failed_at_ms = now_ms,
                    .raw_payload = std::string(raw_input)
                });
        }

        // 6. Побудова чистої канонічної моделі
        CanonicalOrderMessage msg{
            .message_id = generate_id("msg", now_ms),
            .correlation_id = std::string(correlation_id.empty() ? "unknown-trace" : correlation_id),
            .timestamp_ms = now_ms,
            .schema_version = 1,
            .order_id = order_id,
            .customer_ref = std::string(tokens[1]),
            .amount_cents = cents,
            .currency = std::string(curr),
            .status = status
        };

        return msg;
    }

    /* 7. Бінарна серіалізація у двійковий формат без динамічних алокацій */
    static std::vector<uint8_t> serialize(const CanonicalOrderMessage& msg) {
        std::vector<uint8_t> buffer;
        buffer.reserve(128 + msg.customer_ref.size());

        // Магічний префікс (0xCF 0x01)
        buffer.push_back(0xCF);
        buffer.push_back(0x01);

        auto append_bytes = [&buffer](const auto& value) {
            const auto* ptr = reinterpret_cast<const uint8_t*>(&value);
            buffer.insert(buffer.end(), ptr, ptr + sizeof(value));
        };

        append_bytes(msg.schema_version);
        append_bytes(msg.timestamp_ms);
        append_bytes(msg.order_id);
        append_bytes(msg.amount_cents);

        buffer.push_back(static_cast<uint8_t>(msg.status));

        // Фіксовані 4 байти під код валюти
        char curr_buf[4] = {0};
        std::copy_n(msg.currency.data(), std::min(size_t{3}, msg.currency.size()), curr_buf);
        buffer.insert(buffer.end(), curr_buf, curr_buf + 4);

        // Довжина та рядок customer_ref
        const auto cust_len = static_cast<uint8_t>(std::min(size_t{255}, msg.customer_ref.size()));
        buffer.push_back(cust_len);
        buffer.insert(buffer.end(), msg.customer_ref.begin(), msg.customer_ref.begin() + cust_len);

        return buffer;
    }
};

} // namespace integration

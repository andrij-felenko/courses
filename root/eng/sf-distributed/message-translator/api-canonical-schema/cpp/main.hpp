#pragma once

#include <cstdint>
#include <span>
#include <string_view>
#include <vector>
#include <expected>
#include <memory>

namespace integration::api {

enum class DlqErrorCode : uint32_t {
    SyntaxMalformed = 1001,
    SchemaValidationFailed = 1002,
    SemanticInvalidCurrency = 2001,
    SemanticUnknownStatus = 2002,
    SemanticInvariantViolation = 2003,
    EnrichmentTimeout = 3001
};

struct DlqErrorRecord {
    DlqErrorCode code;
    std::string_view description;
    std::vector<uint8_t> dlq_payload;
};

struct TranslatorConfig {
    std::string_view source_system_name;
    uint32_t target_schema_version{1};
    bool enable_strict_validation{true};
    size_t scratchpad_buffer_size{64 * 1024};
};

/* Чистий інтерфейс плагіна транслятора */
class IMessageTranslator {
public:
    virtual ~IMessageTranslator() = default;

    /* Гарячий метод обробки: повертає канонічні байти або запис для мертвої черги */
    [[nodiscard]] virtual std::expected<std::vector<uint8_t>, DlqErrorRecord> process_packet(
        std::span<const uint8_t> input_raw_bytes,
        std::string_view traceparent_header
    ) noexcept = 0;
};

/* Фабрика створення екземпляра транслятора з керуванням через smart pointer */
[[nodiscard]] std::unique_ptr<IMessageTranslator> create_translator(
    const TranslatorConfig& config
);

} // namespace integration::api

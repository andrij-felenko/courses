#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <cstdint>

namespace cache::contract {

// Коди помилок побудови ключів кешу
enum class ErrorCode : uint8_t {
    NullParameter,
    InvalidCharacters,
    BufferOverflow,
    EmptyField,
    InvalidVersion,
    InvalidHashTag,
    UnsortedParameters
};

// Підтримувані алгоритми обчислення хеш-дайджестів
enum class DigestAlgorithm : uint8_t {
    None,
    Murmur3_64,
    XXHash64,
    Blake3_128
};

// Вхідна специфікація ключа на базі string_view
struct KeyDescriptor {
    std::string_view namespace_name;
    std::string_view tenant_id;
    std::string_view entity_name;
    std::string_view entity_id;
    std::optional<std::string_view> hash_tag{std::nullopt};
    uint32_t schema_version{1};
    DigestAlgorithm digest_algo{DigestAlgorithm::None};
    std::optional<std::string_view> query_params{std::nullopt};
    std::optional<uint32_t> salt_index{std::nullopt};
};

// Контракт інтерфейсу побудовника ключів
class IKeyBuilder {
public:
    virtual ~IKeyBuilder() = default;

    [[nodiscard]] virtual std::expected<std::string, ErrorCode> build(
        const KeyDescriptor& desc
    ) const noexcept = 0;

    [[nodiscard]] virtual std::expected<std::string_view, ErrorCode> extract_slot_tag(
        std::string_view key
    ) const noexcept = 0;

    [[nodiscard]] virtual bool is_salted(
        std::string_view key,
        uint32_t* out_salt = nullptr
    ) const noexcept = 0;
};

} // namespace cache::contract

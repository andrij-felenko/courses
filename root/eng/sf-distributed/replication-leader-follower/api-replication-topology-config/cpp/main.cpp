#include <span>
#include <string_view>
#include <vector>
#include <cstdint>
#include <expected>

struct MutationRecord {
    std::string_view         datacenter_id;
    uint64_t                 logical_timestamp{0};
    std::span<const uint8_t> payload;
};

struct ConflictResolutionResult {
    std::vector<uint8_t> merged_payload;
    bool                 should_delete{false}; // true = Tombstone маркер
};

/**
 * @brief Ідіоматичний C++20 інтерфейс користувацького злиття конфліктів
 * @param key Ключ сутності
 * @param local Поточний локальний стан рядка
 * @param remote Вхідна мутація з віддаленого датацентру
 * @return Результат злиття або код помилки
 */
std::expected<ConflictResolutionResult, int> resolve_write_conflict(
    std::string_view      key,
    const MutationRecord& local,
    const MutationRecord& remote
);

#include <iostream>
#include <string>
#include <string_view>
#include <cstdint>
#include <expected>

struct InventoryItem {
    std::string sku;
    int32_t available_stock{0};
    int32_t reserved_stock{0};
    uint64_t lock_version{0};
};

enum class ReservationError {
    ItemNotFound,
    InsufficientStock,
    VersionConflict,
    DatabaseFailure
};

class InventoryRepository {
public:
    virtual ~InventoryRepository() = default;
    [[nodiscard]] virtual std::expected<InventoryItem, ReservationError> get_by_sku(std::string_view sku) const = 0;
    [[nodiscard]] virtual std::expected<int64_t, ReservationError> execute_cas_reserve(
        std::string_view sku, int32_t qty, uint64_t expected_version) = 0;
};

class StockService {
public:
    explicit StockService(InventoryRepository& repo) : repo_(repo) {}

    [[nodiscard]] std::expected<void, ReservationError> reserve_stock(std::string_view sku, int32_t qty) {
        // 1. Читання стану сутності без блокувань
        auto item_res = repo_.get_by_sku(sku);
        if (!item_res) {
            return std::unexpected(item_res.error());
        }

        const auto& item = *item_res;

        // 2. Валідація бізнес-правил у пам'яті
        if (item.available_stock < qty) {
            return std::unexpected(ReservationError::InsufficientStock);
        }

        // 3. Атомарне CAS-оновлення
        auto rows_res = repo_.execute_cas_reserve(sku, qty, item.lock_version);
        if (!rows_res) {
            return std::unexpected(rows_res.error());
        }

        // 4. Перевірка колізії конкурентного доступу
        if (*rows_res == 0) {
            return std::unexpected(ReservationError::VersionConflict);
        }

        return {};
    }

private:
    InventoryRepository& repo_;
};

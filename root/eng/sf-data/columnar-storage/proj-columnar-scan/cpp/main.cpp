#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <chrono>
#include <cstdint>
#include <random>
#include <memory>
#include <algorithm>

namespace columnar {

constexpr size_t VECTOR_SIZE = 1024;
constexpr size_t TOTAL_ROWS = 1'000'000;

/* ── Рядкове представлення (NSM) ─────────────────────────────────────────── */
struct RowRecord {
    int64_t user_id{0};
    int32_t amount{0};
    char status[16]{0};
    char description[64]{0}; /* баласт для імітації реального кортежу */
};

class RowTable {
public:
    explicit RowTable(size_t capacity) {
        rows_.reserve(capacity);
    }

    void add_row(const RowRecord& rec) {
        rows_.push_back(rec);
    }

    [[nodiscard]] std::span<const RowRecord> rows() const noexcept {
        return rows_;
    }

    [[nodiscard]] size_t size() const noexcept {
        return rows_.size();
    }

private:
    std::vector<RowRecord> rows_;
};

/* ── Стовпцеве представлення (DSM) ───────────────────────────────────────── */
class ColumnarTable {
public:
    explicit ColumnarTable(size_t capacity) {
        user_ids_.reserve(capacity);
        amounts_.reserve(capacity);
        status_ids_.reserve(capacity);
    }

    uint8_t register_status(std::string_view status) {
        for (size_t i = 0; i < dictionary_.size(); ++i) {
            if (dictionary_[i] == status) {
                return static_cast<uint8_t>(i);
            }
        }
        dictionary_.emplace_back(status);
        return static_cast<uint8_t>(dictionary_.size() - 1);
    }

    void add_record(int64_t uid, int32_t amt, uint8_t status_id) {
        user_ids_.push_back(uid);
        amounts_.push_back(amt);
        status_ids_.push_back(status_id);
    }

    [[nodiscard]] std::span<const int64_t> user_ids() const noexcept { return user_ids_; }
    [[nodiscard]] std::span<const int32_t> amounts() const noexcept { return amounts_; }
    [[nodiscard]] std::span<const uint8_t> status_ids() const noexcept { return status_ids_; }
    [[nodiscard]] const std::vector<std::string>& dictionary() const noexcept { return dictionary_; }
    [[nodiscard]] size_t size() const noexcept { return user_ids_.size(); }

private:
    std::vector<int64_t> user_ids_;
    std::vector<int32_t> amounts_;
    std::vector<uint8_t> status_ids_;
    std::vector<std::string> dictionary_;
};

/* ── 1. Рядковий сканер (Tuple-at-a-time) ─────────────────────────────────── */
size_t scan_row_oriented(const RowTable& table, int32_t min_amount, std::string_view target_status) {
    size_t matches = 0;
    for (const auto& row : table.rows()) {
        if (row.amount > min_amount) {
            if (std::string_view(row.status) == target_status) {
                matches++;
            }
        }
    }
    return matches;
}

/* ── 2. Векторизований стовпцевий сканер із пізньою матеріалізацією ──────── */
size_t scan_columnar_vectorized(const ColumnarTable& table, int32_t min_amount, std::string_view target_status) {
    size_t matches = 0;

    /* Словниковий пошук індексу цільового статусу */
    uint8_t target_id = 0xFF;
    const auto& dict = table.dictionary();
    for (size_t i = 0; i < dict.size(); ++i) {
        if (dict[i] == target_status) {
            target_id = static_cast<uint8_t>(i);
            break;
        }
    }
    if (target_id == 0xFF) return 0;

    const auto total = table.size();
    auto amounts = table.amounts();
    auto statuses = table.status_ids();
    auto user_ids = table.user_ids();

    std::vector<uint16_t> selection_vector(VECTOR_SIZE);

    for (size_t block_start = 0; block_start < total; block_start += VECTOR_SIZE) {
        const size_t block_size = std::min(VECTOR_SIZE, total - block_start);
        size_t sel_count = 0;

        auto amt_chunk = amounts.subspan(block_start, block_size);
        auto st_chunk = statuses.subspan(block_start, block_size);

        /* Етап 1: Векторна фільтрація за стовпцями amount та status */
        for (size_t i = 0; i < block_size; ++i) {
            const bool pass = (amt_chunk[i] > min_amount) & (st_chunk[i] == target_id);
            if (pass) {
                selection_vector[sel_count++] = static_cast<uint16_t>(i);
            }
        }

        /* Етап 2: Пізня матеріалізація для відфільтрованого вектора індексів */
        for (size_t j = 0; j < sel_count; ++j) {
            const size_t global_idx = block_start + selection_vector[j];
            [[maybe_unused]] auto uid = user_ids[global_idx];
            [[maybe_unused]] auto amt = amounts[global_idx];
            matches++;
        }
    }

    return matches;
}

} // namespace columnar

int main() {
    using namespace columnar;
    std::cout << "Генерація " << TOTAL_ROWS << " тестових транзакцій (C++)...\n";

    RowTable row_tbl(TOTAL_ROWS);
    ColumnarTable col_tbl(TOTAL_ROWS);

    const std::vector<std::string> status_labels = { "PENDING", "PAID", "CANCELLED", "REFUNDED" };
    for (const auto& s : status_labels) {
        col_tbl.register_status(s);
    }

    std::mt19937 gen(42);
    std::uniform_int_distribution<int32_t> amt_dist(0, 999);
    std::uniform_int_distribution<size_t> st_dist(0, status_labels.size() - 1);

    for (size_t i = 0; i < TOTAL_ROWS; ++i) {
        int64_t uid = 1'000'000 + static_cast<int64_t>(i);
        int32_t amt = amt_dist(gen);
        size_t st_idx = st_dist(gen);

        RowRecord rec{};
        rec.user_id = uid;
        rec.amount = amt;
        std::snprintf(rec.status, sizeof(rec.status), "%s", status_labels[st_idx].c_str());
        std::snprintf(rec.description, sizeof(rec.description), "Tx payload #%zu", i);
        row_tbl.add_row(rec);

        col_tbl.add_record(uid, amt, static_cast<uint8_t>(st_idx));
    }

    constexpr int32_t filter_amt = 500;
    constexpr std::string_view filter_status = "PAID";

    auto t0 = std::chrono::high_resolution_clock::now();
    size_t count_row = scan_row_oriented(row_tbl, filter_amt, filter_status);
    auto t1 = std::chrono::high_resolution_clock::now();
    double time_row_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    auto t2 = std::chrono::high_resolution_clock::now();
    size_t count_col = scan_columnar_vectorized(col_tbl, filter_amt, filter_status);
    auto t3 = std::chrono::high_resolution_clock::now();
    double time_col_ms = std::chrono::duration<double, std::milli>(t3 - t2).count();

    std::cout << "\n=== Результати сканування (C++) ===\n";
    std::cout << "Рядковий підхід (NSM):      " << count_row << " збігів за " << time_row_ms << " мс\n";
    std::cout << "Стовпцевий векторизований:  " << count_col << " збігів за " << time_col_ms << " мс\n";
    std::cout << "Прискорення:                " << (time_row_ms / (time_col_ms > 0 ? time_col_ms : 0.001)) << "x\n";

    return 0;
}

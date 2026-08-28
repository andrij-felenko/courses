#include <cstdint>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using Id    = std::int64_t;
using Money = std::int64_t;   // гроші — цілі копійки, ніяких double
using Day   = std::int32_t;   // дата — номер доби від епохи

enum class RowState : std::uint8_t { Unchanged, Added, Modified, Deleted };

// Таблиця набору рядків: рядки + мітка стану на кожен + два індекси.
// Від Row вимагається одне поле — Id id, це первинний ключ.
template <class Row>
class Table {
public:
    struct Change { RowState state; const Row* row; };

    void load(Row r)   { add(std::move(r), RowState::Unchanged); }  // приїхало з бази
    void insert(Row r) { add(std::move(r), RowState::Added); }      // народилося тут

    const Row* find(Id id) const {                   // ← це місце вирішує все
        auto it = index_.find(id);
        return it == index_.end() ? nullptr : &rows_[it->second];
    }

    Row* modify(Id id) {                             // те саме, але з міткою «змінено»
        auto it = index_.find(id);
        if (it == index_.end()) return nullptr;
        touch(it->second);
        return &rows_[it->second];
    }

    void erase(Id id) {
        auto it = index_.find(id);
        if (it == index_.end()) return;
        touch(it->second);
        state_[it->second] = RowState::Deleted;      // не викидаємо: базі ще треба сказати
    }

    std::size_t size() const               { return rows_.size(); }
    const Row&  at(std::size_t i) const    { return rows_[i]; }
    bool        alive(std::size_t i) const { return state_[i] != RowState::Deleted; }

    void indexBy(Id Row::* column) { column_ = column; rebuild(); }   // вторинний індекс

    const std::vector<std::size_t>& rowsWith(Id key) const {
        static const std::vector<std::size_t> none;
        auto it = secondary_.find(key);
        return it == secondary_.end() ? none : it->second;
    }

    std::vector<Change> changes() const {
        std::vector<Change> out;
        for (std::size_t i = 0; i < rows_.size(); ++i)
            if (state_[i] != RowState::Unchanged) out.push_back({state_[i], &rows_[i]});
        return out;
    }

    void accept() {                                  // база прийняла все
        std::vector<Row> kept;
        kept.reserve(rows_.size());
        for (std::size_t i = 0; i < rows_.size(); ++i)
            if (state_[i] != RowState::Deleted) kept.push_back(std::move(rows_[i]));
        settle(std::move(kept));
    }

    void reject() {                                  // назад до вихідних значень
        std::vector<Row> kept;
        for (std::size_t i = 0; i < rows_.size(); ++i) {
            if (state_[i] == RowState::Added) continue;          // доданого не було
            auto o = original_.find(rows_[i].id);
            kept.push_back(o == original_.end() ? std::move(rows_[i]) : std::move(o->second));
        }
        settle(std::move(kept));
    }

private:
    void add(Row r, RowState st) {
        if (index_.count(r.id)) throw std::logic_error("дубль первинного ключа");
        const std::size_t slot = rows_.size();
        index_.emplace(r.id, slot);
        if (column_) secondary_[r.*column_].push_back(slot);
        rows_.push_back(std::move(r));
        state_.push_back(st);
    }

    void touch(std::size_t i) {
        if (state_[i] == RowState::Unchanged) {
            original_.emplace(rows_[i].id, rows_[i]);   // копія вихідного — щоб було що вертати
            state_[i] = RowState::Modified;
        }
    }

    void settle(std::vector<Row> kept) {
        rows_ = std::move(kept);
        state_.assign(rows_.size(), RowState::Unchanged);
        original_.clear();
        rebuild();
    }

    void rebuild() {                                 // слоти зсунулися — індекси наново
        index_.clear();
        secondary_.clear();
        for (std::size_t i = 0; i < rows_.size(); ++i) {
            index_[rows_[i].id] = i;
            if (column_) secondary_[rows_[i].*column_].push_back(i);
        }
    }

    std::vector<Row>      rows_;     // колонки — поля структури, перевірені компілятором
    std::vector<RowState> state_;    // мітка на кожен рядок, паралельним масивом
    std::unordered_map<Id, std::size_t>              index_;      // id → слот
    std::unordered_map<Id, std::vector<std::size_t>> secondary_;  // чужий ключ → слоти
    std::unordered_map<Id, Row>                      original_;   // вихідні значення змінених
    Id Row::* column_ = nullptr;
};

struct Product     { Id id; std::string kind; };
struct Contract    { Id id; Id productId; Money revenue; Day signedOn; };
struct Recognition { Id id; Id contractId; Money amount; Day on; };

struct SalesData {                                   // це і є набір рядків застосунку
    Table<Product>     products;
    Table<Contract>    contracts;
    Table<Recognition> recognitions;
    Id nextTempId = -1;        // тимчасові ключі від'ємні: справжні роздасть база
};

inline SalesData makeSalesData() {
    SalesData d;
    d.recognitions.indexBy(&Recognition::contractId);   // без цього «усі рядки контракту»
    return d;                                           // тихо стає перебором
}

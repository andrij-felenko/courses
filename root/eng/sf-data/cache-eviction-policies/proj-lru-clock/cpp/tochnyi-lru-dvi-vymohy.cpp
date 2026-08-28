#include <cstdint>
#include <optional>
#include <unordered_map>
#include <vector>

// Точний LRU зі стелею в cap записів.
// Вузли лежать у суцільному масиві; зв'язки — номери слотів, а не покажчики.
template <class K, class V>
class LruCache {
    static constexpr uint32_t NIL = 0xFFFFFFFFu;
    struct Node { K key; V val; uint32_t prev = NIL, next = NIL; };

    std::vector<Node> slots_;                 // усі записи живуть тут
    std::unordered_map<K, uint32_t> index_;   // ключ → номер слота
    uint32_t head_ = NIL, tail_ = NIL, cap_;
    uint64_t hits_ = 0, misses_ = 0, evictions_ = 0;

public:
    explicit LruCache(uint32_t cap) : cap_(cap) {
        slots_.reserve(cap_);       // жодного перерозподілу за весь час життя
        index_.reserve(cap_ * 2);   // щоб таблиця не перебудовувалася на ходу
    }

    // Значення повертаємо КОПІЄЮ: посилання назовні віддавати не можна —
    // наступний put може витіснити саме цей запис і перевикористати слот.
    std::optional<V> get(const K& key) {
        auto it = index_.find(key);
        if (it == index_.end()) { ++misses_; return std::nullopt; }
        ++hits_;
        touch(it->second);                    // ЧИТАННЯ, ЯКЕ ПИШЕ
        return slots_[it->second].val;
    }

    void put(const K& key, V val) {
        if (auto it = index_.find(key); it != index_.end()) {
            slots_[it->second].val = std::move(val);
            touch(it->second);
            return;
        }
        uint32_t i;
        if (slots_.size() < cap_) {           // кеш іще не повний — новий слот
            i = static_cast<uint32_t>(slots_.size());
            slots_.emplace_back();
        } else {                              // повний — жертва з хвоста
            i = tail_;
            unlink(i);
            index_.erase(slots_[i].key);      // ключ ще живий: слот не чіпали
            ++evictions_;
        }
        slots_[i].key = key;
        slots_[i].val = std::move(val);
        index_.emplace(key, i);
        push_front(i);
    }

    double hit_ratio() const {
        uint64_t n = hits_ + misses_;
        return n ? static_cast<double>(hits_) / static_cast<double>(n) : 0.0;
    }

private:
    void unlink(uint32_t i) {
        Node& n = slots_[i];
        (n.prev == NIL ? head_ : slots_[n.prev].next) = n.next;
        (n.next == NIL ? tail_ : slots_[n.next].prev) = n.prev;
        n.prev = n.next = NIL;
    }

    void push_front(uint32_t i) {
        Node& n = slots_[i];
        n.prev = NIL;
        n.next = head_;
        if (head_ != NIL) slots_[head_].prev = i;
        head_ = i;
        if (tail_ == NIL) tail_ = i;
    }

    void touch(uint32_t i) {
        if (i == head_) return;               // найсвіжіший — робити нічого
        unlink(i);
        push_front(i);
    }
};

#include <cstdint>
#include <optional>
#include <string>
#include <utility>
#include <vector>

class Map {
    struct Node {
        std::string key;
        int64_t val;
        Node* next;
    };

    static constexpr size_t kInitCap = 8; // степінь двійки

    std::vector<Node*> buckets_;
    size_t n_;

    // Байти беремо як unsigned char: у char (знаковому на більшості платформ)
    // байт ≥ 128 розширився б знаком і зіпсував старші біти хешу.
    static uint32_t hash(const std::string& key) {
        uint32_t h = 2166136261u;
        for (unsigned char c : key) {
            h ^= c;
            h *= 16777619u; // переповнення uint32 тут навмисне
        }
        return h ^ (h >> 16);
    }

    size_t index(uint32_t h) const { return h & (buckets_.size() - 1); }

    void grow() {
        std::vector<Node*> old = std::move(buckets_);
        buckets_.assign(old.size() * 2, nullptr); // нова місткість — ДО переіндексації
        for (Node* p : old) {
            while (p) {
                Node* next = p->next; // зберегти: зараз перечепимо p->next
                size_t i = index(hash(p->key));
                p->next = buckets_[i];
                buckets_[i] = p;
                p = next;
            }
        }
        // n_ не чіпаємо: вузли переїхали, нових пар не з'явилося
    }

public:
    Map() : buckets_(kInitCap, nullptr), n_(0) {}

    ~Map() {
        for (Node* p : buckets_)
            while (p) { Node* next = p->next; delete p; p = next; }
    }

    // вузли тримаємо сирими вказівниками — копіювання дало б подвійне звільнення
    Map(const Map&) = delete;
    Map& operator=(const Map&) = delete;

    std::optional<int64_t> get(const std::string& key) const {
        for (Node* p = buckets_[index(hash(key))]; p; p = p->next)
            if (p->key == key) // звіряємо ПОВНИЙ ключ, не хеш
                return p->val;
        return std::nullopt;
    }

    void put(const std::string& key, int64_t val) {
        size_t i = index(hash(key));
        for (Node* p = buckets_[i]; p; p = p->next)
            if (p->key == key) {
                p->val = val; // оновлення наявного: n_ НЕ росте
                return;
            }
        buckets_[i] = new Node{key, val, buckets_[i]}; // у голову
        ++n_;
        if (4 * n_ > 3 * buckets_.size()) grow();
    }

    bool remove(const std::string& key) {
        size_t i = index(hash(key));
        Node* prev = nullptr;
        for (Node* p = buckets_[i]; p; prev = p, p = p->next)
            if (p->key == key) {
                if (prev) prev->next = p->next;
                else buckets_[i] = p->next; // видаляємо голову
                delete p;                   // без цього — витік пам'яті
                --n_;
                return true;
            }
        return false;
    }

    size_t size() const { return n_; }
};

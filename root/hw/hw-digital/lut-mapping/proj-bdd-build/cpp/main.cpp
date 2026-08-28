#include <cstddef>
#include <cstdint>
#include <unordered_map>
#include <vector>

enum : uint32_t { FALSE_ID = 0, TRUE_ID = 1 };   // не FALSE/TRUE: то макроси у <windows.h>

// Вузол — три 32-бітні поля, 12 байтів. Жодних вказівників: id вузла — це індекс
// у векторі, тож він удвічі вужчий за вказівник і не з'їжджає після realloc.
struct Node {
    uint32_t var, lo, hi;
    bool operator==(const Node& o) const noexcept {
        return var == o.var && lo == o.lo && hi == o.hi;
    }
};

struct NodeHash {                                 // FNV-подібне змішування трьох полів
    std::size_t operator()(const Node& n) const noexcept {
        uint64_t h = 0xCBF29CE484222325ull;
        h = (h ^ n.var) * 0x100000001B3ull;
        h = (h ^ n.lo)  * 0x100000001B3ull;
        h = (h ^ n.hi)  * 0x100000001B3ull;
        return static_cast<std::size_t>(h ^ (h >> 29));
    }
};

class Bdd {
public:
    Bdd() {
        nodes_.resize(2);                         // 0 і 1 — термінали, тіла їм не треба
        unique_.reserve(1u << 16);                // місце наперед: рехеш на гарячому шляху дорогий
    }

    uint32_t make_node(uint32_t var, uint32_t lo, uint32_t hi) {
        if (lo == hi) return lo;                                  // правило 1
        const Node key{var, lo, hi};
        if (auto it = unique_.find(key); it != unique_.end())
            return it->second;                                    // правило 2
        const uint32_t id = static_cast<uint32_t>(nodes_.size());
        nodes_.push_back(key);
        unique_.emplace(key, id);
        return id;
    }

    const Node& at(uint32_t id) const { return nodes_[id]; }
    bool terminal(uint32_t id) const { return id <= TRUE_ID; }
    std::size_t size() const { return nodes_.size(); }

private:
    std::vector<Node> nodes_;
    std::unordered_map<Node, uint32_t, NodeHash> unique_;
};

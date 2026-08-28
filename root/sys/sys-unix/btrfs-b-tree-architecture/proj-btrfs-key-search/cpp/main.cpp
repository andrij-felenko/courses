#include <iostream>
#include <vector>
#include <span>
#include <compare>
#include <algorithm>
#include <optional>
#include <cstdint>

enum class KeyType : uint8_t {
    InodeItem = 1,
    InodeRef = 12,
    XattrItem = 24,
    ExtentData = 108
};

// 3-компонентний ключ Btrfs із C++20 трьохстороннім порівнянням (spaceship operator)
struct BtrfsKey {
    uint64_t objectid;
    KeyType type;
    uint64_t offset;

    auto operator<=>(const BtrfsKey&) const = default;
};

struct BtrfsItem {
    BtrfsKey key;
    uint32_t offset;
    uint32_t size;
};

// Клас-модель листка Btrfs: незалежний перегляд (span) і явний результат пошуку
class BtrfsLeafView {
private:
    std::span<const BtrfsItem> items_;

public:
    explicit BtrfsLeafView(std::span<const BtrfsItem> items) : items_(items) {}

    struct SearchResult {
        size_t slot;
        bool exact_match;
    };

    [[nodiscard]] SearchResult search(const BtrfsKey& target) const {
        auto it = std::lower_bound(
            items_.begin(), items_.end(), target,
            [](const BtrfsItem& item, const BtrfsKey& key) {
                return item.key < key;
            }
        );

        size_t slot = std::distance(items_.begin(), it);
        bool exact = (it != items_.end() && it->key == target);

        return {slot, exact};
    }
};

int main() {
    const std::vector<BtrfsItem> leaf_items = {
        { {257, KeyType::InodeItem, 0},          16123, 160 },
        { {257, KeyType::InodeRef, 256},         16107, 16 },
        { {257, KeyType::XattrItem, 0x8a9b1c2d}, 16067, 40 },
        { {257, KeyType::ExtentData, 0},         16014, 53 },
        { {257, KeyType::ExtentData, 4096},      15961, 53 },
        { {258, KeyType::InodeItem, 0},          15801, 160 }
    };

    BtrfsLeafView leaf(leaf_items);

    BtrfsKey search_key{257, KeyType::ExtentData, 4096};
    auto [slot, exact] = leaf.search(search_key);

    if (exact) {
        std::cout << "Знайдено елемент у слоті " << slot
                  << " (objectid=" << leaf_items[slot].key.objectid
                  << ", offset=" << leaf_items[slot].key.offset << ")\n";
    } else {
        std::cout << "Елемент відсутній. Слот вставки: " << slot << "\n";
    }

    return 0;
}

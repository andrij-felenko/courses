#include <memory>
#include <shared_mutex>
#include <unordered_map>

struct KindKey {                          // складений ключ відкритої множини
    std::string species;
    uint8_t     season;                   // 0..3
    uint8_t     lod;                      // 0..3
    bool operator==(const KindKey&) const = default;
};
struct KindKeyHash {
    std::size_t operator()(const KindKey& k) const {
        std::size_t h = std::hash<std::string>{}(k.species);
        h = h * 31 + k.season;            // дешево поєднуємо доданки ключа
        h = h * 31 + k.lod;
        return h;
    }
};

class WeakKindFactory {
    std::shared_mutex mtx_;
    std::unordered_map<KindKey, std::weak_ptr<const TreeKind>, KindKeyHash> pool_;
public:
    // Повертає СИЛЬНЕ посилання — його триматиме дерево-власник.
    std::shared_ptr<const TreeKind> get(const KindKey& key) {
        {   // швидкий шлях: читачі паралельно
            std::shared_lock read(mtx_);
            if (auto it = pool_.find(key); it != pool_.end())
                if (auto sp = it->second.lock())      // ще живий?
                    return sp;
        }
        std::unique_lock write(mtx_);
        if (auto it = pool_.find(key); it != pool_.end())
            if (auto sp = it->second.lock())          // повторна перевірка
                return sp;
        auto sp = std::make_shared<const TreeKind>(load_tree_kind(key));
        pool_[key] = sp;                              // фабрика тримає СЛАБКЕ
        return sp;                                    // сильне йде власникові
    }

    // Прибрати «протухлі» записи — інакше ростуть самі ключі.
    void prune() {
        std::unique_lock write(mtx_);
        for (auto it = pool_.begin(); it != pool_.end(); )
            it = it->second.expired() ? pool_.erase(it) : std::next(it);
    }
};

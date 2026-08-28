#include <shared_mutex>

class TreeKindFactory {
    mutable std::shared_mutex mtx_;
    std::unordered_map<std::string, std::unique_ptr<TreeKind>> pool_;
public:
    const TreeKind* get(const std::string& name) {
        {   // ── швидкий шлях: багато читачів ПАРАЛЕЛЬНО ──
            std::shared_lock read(mtx_);
            if (auto it = pool_.find(name); it != pool_.end())
                return it->second.get();
        }
        // ── промах: рідкісний ЕКСКЛЮЗИВНИЙ запис ──
        std::unique_lock write(mtx_);
        // ПОВТОРНА перевірка: поки ми відпускали read і брали write,
        // інший потік міг уже вставити цей самий вид.
        if (auto it = pool_.find(name); it != pool_.end())
            return it->second.get();
        auto kind = load_tree_kind(name);
        const TreeKind* raw = kind.get();
        pool_.emplace(name, std::move(kind));
        return raw;
    }
};

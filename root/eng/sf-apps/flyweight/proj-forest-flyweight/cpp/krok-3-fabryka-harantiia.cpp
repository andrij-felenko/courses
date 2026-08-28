#include <memory>
#include <unordered_map>

class TreeKindFactory {
    std::unordered_map<std::string, std::unique_ptr<TreeKind>> pool_;
public:
    const TreeKind* get(const std::string& name) {
        if (auto it = pool_.find(name); it != pool_.end())
            return it->second.get();               // уже є — той самий примірник
        auto kind = load_tree_kind(name);          // нема — дорого читаємо з диска РАЗ
        const TreeKind* raw = kind.get();
        pool_.emplace(name, std::move(kind));
        return raw;
    }
};

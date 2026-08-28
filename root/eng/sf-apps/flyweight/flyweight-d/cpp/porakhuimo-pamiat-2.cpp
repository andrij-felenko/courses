class TreeKindFactory {
    std::unordered_map<std::string, std::unique_ptr<TreeKind>> pool_;
public:
    const TreeKind* get(const std::string& name) {
        auto it = pool_.find(name);
        if (it != pool_.end()) return it->second.get();  // уже є — той самий примірник
        auto kind = loadTreeKind(name);                  // нема — створити РАЗ
        const TreeKind* raw = kind.get();
        pool_[name] = std::move(kind);
        return raw;
    }
};

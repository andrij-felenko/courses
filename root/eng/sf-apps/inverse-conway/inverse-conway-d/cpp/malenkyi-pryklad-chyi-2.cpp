// Каталог володіє кешем і дає назовні лише контракт.
// billing НЕ бачить ні mu, ні map — лише ці дві функції.
class CatalogCache {
public:
    std::optional<Value> get(const Key& k) const;   // весь замок — усередині
    void                 put(const Key& k, Value v);
private:
    mutable std::mutex   mu_;
    std::map<Key, Value> data_;                      // нутро закрите
};

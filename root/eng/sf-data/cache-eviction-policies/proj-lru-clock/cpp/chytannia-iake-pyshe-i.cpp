template <class K, class V>
class LockedLru {
    LruCache<K, V> impl_;
    std::mutex mu_;                     // shared_mutex тут НЕ допоможе

public:
    std::optional<V> get(const K& key) {
        std::lock_guard lk(mu_);        // ексклюзивний навіть на читанні
        return impl_.get(key);
    }
    void put(const K& key, V val) {
        std::lock_guard lk(mu_);
        impl_.put(key, std::move(val));
    }
};

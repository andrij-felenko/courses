template <
    typename Key,
    typename Value,
    typename Hash1 = DefaultHash1<Key>,
    typename Hash2 = DefaultHash2<Key>
>
class CuckooMap {
public:
    using key_type = Key;
    using mapped_type = Value;
    using value_type = std::pair<const Key, Value>;
    using size_type = std::size_t;

    explicit CuckooMap(size_type initial_capacity = 16);
    ~CuckooMap() = default;

    CuckooMap(const CuckooMap &other);
    CuckooMap(CuckooMap &&other) noexcept;
    CuckooMap &operator=(const CuckooMap &other);
    CuckooMap &operator=(CuckooMap &&other) noexcept;

    [[nodiscard]] std::optional<Value> find(const Key &key) const;
    [[nodiscard]] bool contains(const Key &key) const noexcept;

    CuckooStatus insert(const Key &key, const Value &value);
    CuckooStatus insert_or_assign(const Key &key, const Value &value);

    bool erase(const Key &key);
    void clear() noexcept;

    [[nodiscard]] size_type size() const noexcept;
    [[nodiscard]] size_type capacity() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] CuckooStats stats() const noexcept;
};

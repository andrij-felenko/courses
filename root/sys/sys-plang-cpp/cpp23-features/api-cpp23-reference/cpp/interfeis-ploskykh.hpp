namespace std {

template <
    class Key,
    class T,
    class Compare = less<Key>,
    class KeyContainer = vector<Key>,
    class MappedContainer = vector<T>
>
class flat_map {
public:
    using key_type = Key;
    using mapped_type = T;
    using value_type = pair<key_type, mapped_type>;
    using key_compare = Compare;
    using key_container_type = KeyContainer;
    using mapped_container_type = MappedContainer;
    using size_type = size_t;
    using difference_type = ptrdiff_t;
    using reference = pair<const key_type&, mapped_type&>;
    using const_reference = pair<const key_type&, const mapped_type&>;

    struct containers {
        key_container_type keys;
        mapped_container_type values;
    };

    // Конструктори
    flat_map();
    explicit flat_map(const Compare& comp);
    flat_map(key_container_type keys, mapped_container_type values, const Compare& comp = Compare());

    // Вилучення та заміна базових векторів
    containers extract() &&;
    void replace(key_container_type keys, mapped_container_type values);

    // Доступ до елементів за ключем
    mapped_type& at(const key_type& k);
    const mapped_type& at(const key_type& k) const;
    mapped_type& operator[](const key_type& k);
    mapped_type& operator[](key_type&& k);

    // Операції пошуку O(log N)
    iterator find(const key_type& k);
    const_iterator find(const key_type& k) const;
    bool contains(const key_type& k) const;
    size_type count(const key_type& k) const;

    // Вставка зі збереженням сортування O(N)
    pair<iterator, bool> insert(const value_type& x);
    pair<iterator, bool> insert(value_type&& x);
    template <class... Args>
    pair<iterator, bool> emplace(Args&&... args);

    // Доступ до внутрішніх контейнерів
    const key_container_type& keys() const noexcept;
    const mapped_container_type& values() const noexcept;
};

} // namespace std

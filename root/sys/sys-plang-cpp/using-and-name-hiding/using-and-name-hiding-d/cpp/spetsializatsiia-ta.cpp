template <typename T>
struct StorageTraits {
    using type = T;
};

template <>
struct StorageTraits<bool> {
    using type = uint8_t; // оптимізація бітового представлення
};

template <typename T>
using StorageType = typename StorageTraits<T>::type;

namespace detail {
    // Гілка 1: Швидкий memcpy для тривіально копійованих типів
    template<typename T>
    void copy_impl(const T* src, T* dst, std::size_t count, std::true_type) {
        std::memcpy(dst, src, count * sizeof(T));
    }

    // Гілка 2: Поелементний цикл для складних типів
    template<typename T>
    void copy_impl(const T* src, T* dst, std::size_t count, std::false_type) {
        for (std::size_t i = 0; i < count; ++i) {
            dst[i] = src[i];
        }
    }
}

template<typename T>
void copy_buffer(const T* src, T* dst, std::size_t count) {
    detail::copy_impl(src, dst, count, std::is_trivially_copyable<T>());
}

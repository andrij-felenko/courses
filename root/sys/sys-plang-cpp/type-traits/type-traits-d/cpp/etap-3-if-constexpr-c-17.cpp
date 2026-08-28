template<typename T>
void copy_buffer(const T* src, T* dst, std::size_t count) {
    if constexpr (std::is_trivially_copyable_v<T>) {
        // Миттєве копіювання блоку пам'яті
        std::memcpy(dst, src, count * sizeof(T));
    } else {
        // Поелементний виклик операторів присвоєння
        for (std::size_t i = 0; i < count; ++i) {
            dst[i] = src[i];
        }
    }
}

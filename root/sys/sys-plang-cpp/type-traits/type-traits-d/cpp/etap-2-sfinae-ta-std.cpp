// Гілка 1: Активується тільки якщо тип тривіально копійований
template<typename T, std::enable_if_t<std::is_trivially_copyable_v<T>>* = nullptr>
void copy_buffer(const T* src, T* dst, std::size_t count) {
    std::memcpy(dst, src, count * sizeof(T));
}

// Гілка 2: Активується тільки якщо тип НЕ є тривіально копійованим
template<typename T, std::enable_if_t<!std::is_trivially_copyable_v<T>>* = nullptr>
void copy_buffer(const T* src, T* dst, std::size_t count) {
    for (std::size_t i = 0; i < count; ++i) {
        dst[i] = src[i];
    }
}

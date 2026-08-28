namespace tags {
    struct FastMemcpyTag {};
    struct ElementWiseTag {};
}

template<typename T>
void copy_buffer_impl(const T* src, T* dst, std::size_t n, tags::FastMemcpyTag) {
    std::memcpy(dst, src, n * sizeof(T));
}

template<typename T>
void copy_buffer_impl(const T* src, T* dst, std::size_t n, tags::ElementWiseTag) {
    for (std::size_t i = 0; i < n; ++i) {
        dst[i] = src[i];
    }
}

template<typename T>
void copy_buffer(const T* src, T* dst, std::size_t n) {
    using Tag = std::conditional_t<
        std::is_trivially_copyable_v<T>,
        tags::FastMemcpyTag,
        tags::ElementWiseTag
    >;
    copy_buffer_impl(src, dst, n, Tag{});
}

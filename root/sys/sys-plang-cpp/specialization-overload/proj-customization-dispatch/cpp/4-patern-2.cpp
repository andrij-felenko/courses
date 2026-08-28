namespace tag_dispatch_design {

// Оголошення типів-тегів
struct ContiguousMemoryTag {};
struct ElementWiseMemoryTag {};

// Метафункція для вибору тегу під час компіляції
template<typename T>
struct MemoryLayoutCategory {
    using type = std::conditional_t<
        std::is_trivially_copyable_v<T> && (std::endian::native == std::endian::big || sizeof(T) == 1),
        ContiguousMemoryTag,
        ElementWiseMemoryTag
    >;
};

template<typename T>
using MemoryLayoutCategory_t = typename MemoryLayoutCategory<T>::type;

// Внутрішня гілка 1: швидке суцільне копіювання пам'яті
template<typename T>
void write_buffer_impl(BinaryBuffer& buf, const T* data, std::size_t count, ContiguousMemoryTag) {
    buf.write_raw(data, count * sizeof(T));
}

// Внутрішня гілка 2: поелементна серіалізація для складних типів
template<typename T>
void write_buffer_impl(BinaryBuffer& buf, const T* data, std::size_t count, ElementWiseMemoryTag) {
    for (std::size_t i = 0; i < count; ++i) {
        trait_design::serialize(buf, data[i]);
    }
}

// Публічна функція серіалізації масиву
template<typename T>
void serialize_contiguous_span(BinaryBuffer& buf, std::span<const T> elements) {
    uint32_t count = static_cast<uint32_t>(elements.size());
    buf.write_raw(&count, sizeof(count));
    
    // Компілятор обирає потрібне перевантаження за типом третього аргументу-тегу
    write_buffer_impl(buf, elements.data(), elements.size(), MemoryLayoutCategory_t<T>{});
}

} // namespace tag_dispatch_design

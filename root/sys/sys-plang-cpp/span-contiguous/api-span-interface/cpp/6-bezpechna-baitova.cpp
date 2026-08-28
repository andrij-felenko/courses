namespace std {
    template <typename ElementType, std::size_t Extent>
    span<const std::byte, 
         Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_bytes(span<ElementType, Extent> s) noexcept;

    template <typename ElementType, std::size_t Extent>
    requires (!std::is_const_v<ElementType>)
    span<std::byte, 
         Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_writable_bytes(span<ElementType, Extent> s) noexcept;
}

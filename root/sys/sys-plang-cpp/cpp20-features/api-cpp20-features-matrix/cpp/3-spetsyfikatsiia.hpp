namespace std {
    inline constexpr size_t dynamic_extent = numeric_limits<size_t>::max();

    template<typename ElementType, size_t Extent = dynamic_extent>
    class span {
    public:
        using element_type     = ElementType;
        using value_type       = remove_cv_t<ElementType>;
        using size_type        = size_t;
        using difference_type  = ptrdiff_t;
        using pointer          = ElementType*;
        using const_pointer    = const ElementType*;
        using reference        = ElementType&;
        using const_reference  = const ElementType&;
        using iterator         = /* contiguous iterator */;

        static constexpr size_t extent = Extent;

        // Конструктори
        constexpr span() noexcept;
        constexpr span(pointer ptr, size_type count);
        constexpr span(pointer first, pointer last);
        template<size_t N>
        constexpr span(element_type (&arr)[N]) noexcept;
        template<typename Container>
        constexpr span(Container& cont);

        // Доступ до елементів
        constexpr reference front() const;
        constexpr reference back() const;
        constexpr reference operator[](size_type idx) const;
        constexpr pointer data() const noexcept;

        // Розмір та стан
        constexpr size_type size() const noexcept;
        constexpr size_type size_bytes() const noexcept;
        [[nodiscard]] constexpr bool empty() const noexcept;

        // Піддіапазони
        template<size_t Count>
        constexpr span<element_type, Count> first() const;
        constexpr span<element_type, dynamic_extent> first(size_type count) const;

        template<size_t Count>
        constexpr span<element_type, Count> last() const;
        constexpr span<element_type, dynamic_extent> last(size_type count) const;

        template<size_t Offset, size_t Count = dynamic_extent>
        constexpr auto subspan() const;
        constexpr span<element_type, dynamic_extent>
        subspan(size_type offset, size_type count = dynamic_extent) const;
    };
}

namespace gsl {
    inline constexpr std::ptrdiff_t dynamic_extent = -1;

    template <class ElementType, std::ptrdiff_t Extent = dynamic_extent>
    class span {
    public:
        using element_type     = ElementType;
        using value_type       = std::remove_cv_t<ElementType>;
        using size_type        = std::ptrdiff_t; // Знаковий тип індексу
        using pointer          = element_type*;
        using const_pointer    = const element_type*;
        using reference        = element_type&;
        using const_reference  = const element_type&;
        using iterator         = /* implementation-defined continuous iterator */;
        using reverse_iterator = std::reverse_iterator<iterator>;

        static constexpr std::ptrdiff_t extent = Extent;

        // Конструктори за замовчуванням та від покажчика з розміром
        constexpr span() noexcept;
        constexpr span(pointer ptr, size_type count);
        constexpr span(pointer firstElem, pointer lastElem);

        // Конструктори від фіксованих масивів мови C
        template <std::size_t N>
        constexpr span(element_type (&arr)[N]) noexcept;

        // Конструктори від стандартних контейнерів (std::vector, std::array)
        template <class Container>
        constexpr span(Container& cont);
        template <class Container>
        constexpr span(const Container& cont);

        // Ітератори суцільного доступу
        constexpr iterator begin() const noexcept;
        constexpr iterator end() const noexcept;
        constexpr reverse_iterator rbegin() const noexcept;
        constexpr reverse_iterator rend() const noexcept;

        // Елементний доступ із обов'язковим контролем меж
        constexpr reference operator[](size_type idx) const;
        constexpr reference front() const;
        constexpr reference back() const;
        constexpr pointer data() const noexcept;

        // Інформація про розмір
        constexpr size_type size() const noexcept;
        constexpr size_type size_bytes() const noexcept;
        [[nodiscard]] constexpr bool empty() const noexcept;

        // Генерація піддіапазонів (Subspans)
        template <std::ptrdiff_t Count>
        constexpr span<element_type, Count> first() const;
        constexpr span<element_type, dynamic_extent> first(size_type count) const;

        template <std::ptrdiff_t Count>
        constexpr span<element_type, Count> last() const;
        constexpr span<element_type, dynamic_extent> last(size_type count) const;

        template <std::ptrdiff_t Offset, std::ptrdiff_t Count = dynamic_extent>
        constexpr auto subspan() const;
        constexpr span<element_type, dynamic_extent> subspan(size_type offset, size_type count = dynamic_extent) const;
    };

    // Допоміжні функції для роботи з сирими байтами
    template <class ElementType, std::ptrdiff_t Extent>
    span<const byte, Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_bytes(span<ElementType, Extent> s) noexcept;

    template <class ElementType, std::ptrdiff_t Extent>
    span<byte, Extent == dynamic_extent ? dynamic_extent : Extent * sizeof(ElementType)>
    as_writeable_bytes(span<ElementType, Extent> s) noexcept;
}

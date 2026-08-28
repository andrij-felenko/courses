namespace std {

inline constexpr size_t dynamic_extent = numeric_limits<size_t>::max();

template <class IndexType, size_t... Extents>
class extents {
public:
    using index_type = IndexType;
    using size_type = size_t;
    using rank_type = size_t;

    static constexpr rank_type rank() noexcept { return sizeof...(Extents); }
    static constexpr rank_type rank_dynamic() noexcept;

    static constexpr size_t static_extent(rank_type r) noexcept;
    constexpr index_type extent(rank_type r) const noexcept;
};

// Зручні псевдоніми для вимірів фіксованого рангу
template <class IndexType, size_t Rank>
using dextents = /* extents з усіма dynamic_extent */;

// Стандартні політики розкладки
struct layout_right {
    template <class Extents> class mapping; // Рядок за рядком (C-style)
};

struct layout_left {
    template <class Extents> class mapping; // Стовпчик за стовпчиком (Fortran-style)
};

struct layout_stride {
    template <class Extents> class mapping; // Довільний фіксований крок для кожного виміру
};

template <
    class ElementType,
    class Extents,
    class LayoutPolicy = layout_right,
    class AccessorPolicy = default_accessor<ElementType>
>
class mdspan {
public:
    using extents_type = Extents;
    using layout_type = LayoutPolicy;
    using accessor_type = AccessorPolicy;
    using mapping_type = typename layout_type::template mapping<extents_type>;
    using element_type = ElementType;
    using value_type = remove_cv_t<element_type>;
    using index_type = typename extents_type::index_type;
    using size_type = typename extents_type::size_type;
    using rank_type = typename extents_type::rank_type;
    using data_handle_type = typename accessor_type::data_handle_type;
    using reference = typename accessor_type::reference;

    // Конструктори
    constexpr mdspan();
    constexpr mdspan(data_handle_type p, const extents_type& ext);
    template <class... IndexTypes>
    constexpr explicit mdspan(data_handle_type p, IndexTypes... dynamic_exts);
    constexpr mdspan(data_handle_type p, const mapping_type& m);
    constexpr mdspan(data_handle_type p, const mapping_type& m, const accessor_type& a);

    // Багатовимірний оператор індексації C++23
    template <class... IndexTypes>
    constexpr reference operator[](IndexTypes... indices) const noexcept;

    // Інспекція властивостей
    static constexpr rank_type rank() noexcept { return extents_type::rank(); }
    static constexpr rank_type rank_dynamic() noexcept { return extents_type::rank_dynamic(); }
    static constexpr size_t static_extent(rank_type r) noexcept { return extents_type::static_extent(r); }
    constexpr index_type extent(rank_type r) const noexcept { return extents_.extent(r); }
    constexpr size_type size() const noexcept;
    constexpr bool empty() const noexcept;

    constexpr data_handle_type data_handle() const noexcept;
    constexpr const mapping_type& mapping() const noexcept;
    constexpr const accessor_type& accessor() const noexcept;
};

} // namespace std

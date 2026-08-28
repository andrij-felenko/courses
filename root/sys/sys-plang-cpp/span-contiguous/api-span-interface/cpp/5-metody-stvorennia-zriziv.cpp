// 1. Перші N елементів
template <std::size_t Count>
constexpr span<element_type, Count> first() const;

constexpr span<element_type, std::dynamic_extent> first(size_type count) const;

// 2. Останні N елементів
template <std::size_t Count>
constexpr span<element_type, Count> last() const;

constexpr span<element_type, std::dynamic_extent> last(size_type count) const;

// 3. Піддіапазон починаючи з Pos розміром Count
template <std::size_t Offset, std::size_t Count = std::dynamic_extent>
constexpr auto subspan() const;

constexpr span<element_type, std::dynamic_extent> 
subspan(size_type offset, size_type count = std::dynamic_extent) const;

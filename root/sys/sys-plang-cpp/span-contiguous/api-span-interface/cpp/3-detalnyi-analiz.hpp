// 1. Конструктор за замовчуванням (тільки якщо Extent == 0 або dynamic_extent)
constexpr span() noexcept;

// 2. З двох ітераторів (first, count або first, last)
template <typename It>
constexpr explicit(Extent != std::dynamic_extent)
span(It first, size_type count);

template <typename It, typename End>
constexpr explicit(Extent != std::dynamic_extent)
span(It first, End last);

// 3. З C-масиву
template <std::size_t N>
constexpr span(element_type (&arr)[N]) noexcept;

// 4. З std::array
template <typename T, std::size_t N>
constexpr span(std::array<T, N>& arr) noexcept;

template <typename T, std::size_t N>
constexpr span(const std::array<T, N>& arr) noexcept;

// 5. З контейнерів (std::vector, std::string тощо) або довільних ranges
template <typename Rng>
constexpr explicit(Extent != std::dynamic_extent)
span(Rng&& range);

// 6. Конструктор конверсії з іншого span (наприклад, з модифікованого у const)
template <typename OtherElementType, std::size_t OtherExtent>
constexpr explicit(Extent != std::dynamic_extent && OtherExtent == std::dynamic_extent)
span(const span<OtherElementType, OtherExtent>& other) noexcept;

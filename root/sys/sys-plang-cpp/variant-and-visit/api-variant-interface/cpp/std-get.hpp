template <typename T, typename... Types>
constexpr T& get(variant<Types...>& v);

template <typename T, typename... Types>
constexpr const T& get(const variant<Types...>& v);

template <typename T, typename... Types>
constexpr T&& get(variant<Types...>&& v);

template <size_t I, typename... Types>
constexpr variant_alternative_t<I, variant<Types...>>& get(variant<Types...>& v);

template <size_t I, typename... Types>
constexpr const variant_alternative_t<I, variant<Types...>>& get(const variant<Types...>& v);

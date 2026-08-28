template <size_t Index, typename T>
struct tuple_leaf {
    COURSES_NO_UNIQUE_ADDRESS T value;
};

template <typename IndexSeq, typename... Ts>
class optimal_tuple_impl;

template <size_t... Indices, typename... Ts>
class optimal_tuple_impl<std::index_sequence<Indices...>, Ts...>
    : private tuple_leaf<Indices, Ts>... {
public:
    // Конструктори та методи доступу get<I>()
};

template <typename... Ts>
using optimal_tuple = optimal_tuple_impl<std::index_sequence_for<Ts...>, Ts...>;

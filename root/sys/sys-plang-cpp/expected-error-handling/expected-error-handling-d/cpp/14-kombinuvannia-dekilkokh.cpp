template <typename T1, typename T2, typename E>
std::expected<std::tuple<T1, T2>, E> expected_zip(
    std::expected<T1, E> e1, 
    std::expected<T2, E> e2) 
{
    return e1.and_then([&](T1&& v1) {
        return e2.transform([&](T2&& v2) {
            return std::make_tuple(std::forward<T1>(v1), std::forward<T2>(v2));
        });
    });
}

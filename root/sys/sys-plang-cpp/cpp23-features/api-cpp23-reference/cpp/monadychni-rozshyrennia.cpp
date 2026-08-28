namespace std {

template <class T>
class optional {
public:
    // and_then: викликає f(*this), якщо значення є; f повинна повертати std::optional<U>
    template <class F>
    constexpr auto and_then(F&& f) &;
    template <class F>
    constexpr auto and_then(F&& f) const &;
    template <class F>
    constexpr auto and_then(F&& f) &&;
    template <class F>
    constexpr auto and_then(F&& f) const &&;

    // transform: викликає f(*this), якщо значення є; загортає результат U у std::optional<U>
    template <class F>
    constexpr auto transform(F&& f) &;
    template <class F>
    constexpr auto transform(F&& f) const &;
    template <class F>
    constexpr auto transform(F&& f) &&;
    template <class F>
    constexpr auto transform(F&& f) const &&;

    // or_else: викликає f(), якщо значення відсутнє; f повинна повертати std::optional<T>
    template <class F>
    constexpr optional<T> or_else(F&& f) const &;
    template <class F>
    constexpr optional<T> or_else(F&& f) &&;
};

} // namespace std

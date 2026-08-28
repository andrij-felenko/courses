// 1. and_then: связує функції, що повертають std::optional<U>
template <class F>
constexpr auto and_then(F&& f) &;

template <class F>
constexpr auto and_then(F&& f) const&;

template <class F>
constexpr auto and_then(F&& f) &&;

template <class F>
constexpr auto and_then(F&& f) const&&;

// 2. transform: застосовує трансформацію T -> U та повертає std::optional<U>
template <class F>
constexpr auto transform(F&& f) &;

template <class F>
constexpr auto transform(F&& f) const&;

template <class F>
constexpr auto transform(F&& f) &&;

template <class F>
constexpr auto transform(F&& f) const&&;

// 3. or_else: надає альтернативне джерело std::optional<T>, якщо поточний порожній
template <class F>
constexpr optional or_else(F&& f) const&;

template <class F>
constexpr optional or_else(F&& f) &&;

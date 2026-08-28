// 1. Конструктор за замовчуванням (умовно explicit)
constexpr explicit(/* див. умови */) pair();

// 2. Конструктор з елементів (умовно explicit)
constexpr explicit(/* див. умови */) pair(const T1& x, const T2& y);

// 3. Шаблонний конструктор з ідеальним передаванням (C++11)
template <typename U1 = T1, typename U2 = T2>
constexpr explicit(/* див. умови */) pair(U1&& x, U2&& y);

// 4. Перетворювальний конструктор копіювання з іншої пари
template <typename U1, typename U2>
constexpr explicit(/* див. умови */) pair(const pair<U1, U2>& p);

// 5. Перетворювальний конструктор переміщення з іншої пари
template <typename U1, typename U2>
constexpr explicit(/* див. умови */) pair(pair<U1, U2>&& p);

// 6. Посекційний конструктор (piecewise construction)
template <typename... Args1, typename... Args2>
constexpr pair(piecewise_construct_t,
               tuple<Args1...> first_args,
               tuple<Args2...> second_args);

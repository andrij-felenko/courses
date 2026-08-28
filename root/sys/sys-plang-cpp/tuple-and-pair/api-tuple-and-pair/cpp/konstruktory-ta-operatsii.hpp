// 1. Конструктор за замовчуванням
constexpr explicit(/* див. умови */) tuple();

// 2. Конструктор з константних посилань
constexpr explicit(/* див. умови */) tuple(const Types&... args);

// 3. Шаблонний конструктор з ідеальним передаванням (універсальні посилання)
template <typename... UTypes>
constexpr explicit(/* див. умови */) tuple(UTypes&&... args);

// 4. Перетворювальний конструктор з іншого tuple
template <typename... UTypes>
constexpr explicit(/* див. умови */) tuple(const tuple<UTypes...>& u);

template <typename... UTypes>
constexpr explicit(/* див. умови */) tuple(tuple<UTypes...>&& u);

// 5. Конструктор конвертації з std::pair (лише для tuple з 2 елементів)
template <typename U1, typename U2>
constexpr explicit(/* див. умови */) tuple(const pair<U1, U2>& p);

template <typename U1, typename U2>
constexpr explicit(/* див. умови */) tuple(pair<U1, U2>&& p);

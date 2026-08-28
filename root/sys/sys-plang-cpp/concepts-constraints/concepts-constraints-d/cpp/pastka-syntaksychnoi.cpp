// Концепт автора бібліотеки A
template<typename T>
concept FastTypeA = sizeof(T) <= 8;

// Концепт автора бібліотеки B
template<typename T>
concept FastTypeB = sizeof(T) <= 8;

template<typename T>
concept SuperFast = FastTypeB<T> && std::is_trivial_v<T>;

template<FastTypeA T>
void run(T obj); // Нормалізовано: Атом 1 (визначений у FastTypeA)

template<SuperFast T>
void run(T obj); // Нормалізовано: Атом 2 (визначений у FastTypeB) && Атом 3

// ПОМИЛКА: хоча тіла FastTypeA та FastTypeB ідентичні за текстом,
// компілятор розглядає їх як різні атоми AST.
// run(10) призведе до ambiguous call!

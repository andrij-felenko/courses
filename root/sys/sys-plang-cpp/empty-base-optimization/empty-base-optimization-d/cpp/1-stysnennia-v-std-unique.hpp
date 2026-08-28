// 1. Звичайне використання зі стандартним безстанним делітером:
std::unique_ptr<int> p1 = std::make_unique<int>(42);
static_assert(sizeof(p1) == sizeof(int*)); // Рівно 8 байтів!

// 2. Використання зі stateless лямбда-функцією (C++20):
auto stateless_del = [](int* p) noexcept { delete p; };
std::unique_ptr<int, decltype(stateless_del)> p2(new int(10), stateless_del);
static_assert(sizeof(p2) == 8); // Стискається в 1 машинне слово!

// 3. Використання зі stateful делітером (наприклад, захоплює контекст арени):
struct ArenaDeleter {
    void* arena_context; // 8 байтів стану
    void operator()(int* p) const noexcept { /* звільнення в арену */ }
};
std::unique_ptr<int, ArenaDeleter> p3(new int(20), ArenaDeleter{nullptr});
static_assert(sizeof(p3) == 16); // Природно зростає до 16 байтів

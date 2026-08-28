#include <utility>                      // std::as_const

struct Person {
    template <class S>
    explicit Person(S&&) { std::printf("шаблон: %s\n", __PRETTY_FUNCTION__); }
    Person(const Person&) { std::puts("копіювальний конструктор"); }
};

Person a{"Ада"};
Person b{a};                    // копія?
Person c{std::as_const(a)};     // теж копія?

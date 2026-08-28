#include <cstdio>
#include <string>
#include <type_traits>

struct Box {
    std::string tag = "box";

    auto viaThis()  const { return [this]  { return tag.size(); }; }   // копія ВКАЗІВНИКА
    auto viaValue() const { return [*this] { return tag.size(); }; }   // копія ОБ'ЄКТА
};

int main() {
    std::string s = "довгий рядок";
    std::string& r = s;                                  // змінна-посилання

    auto byCopy = [r] { return r.size(); };              // поле типу std::string — копія рядка
    static_assert(sizeof(byCopy) >= sizeof(std::string));

    auto counter = [n = 0]() mutable { return ++n; };    // нове поле: auto n = 0
    int first  = counter();
    int second = counter();
    std::printf("%d %d\n", first, second);               // 1 2

    Box box;
    auto keepPtr = box.viaThis();                        // ← тримає адресу box
    auto keepObj = box.viaValue();                       // ← носить власну копію box
    std::printf("%zu %zu\n", keepPtr(), keepObj());      // 3 3

    constexpr int kMax = 100;
    auto noField = [=] { return kMax; };                 // kMax лише прочитано → захоплення немає
    static_assert(std::is_empty_v<decltype(noField)>);
    std::printf("%d\n", noField());                      // 100
}

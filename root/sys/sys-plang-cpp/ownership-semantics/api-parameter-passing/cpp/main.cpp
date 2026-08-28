#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <vector>

struct Widget { std::string name; };

void inspect(const Widget&);            // позичання на читання
void tweak(Widget&);                    // позичання на зміну
void inspect_opt(const Widget*);        // позичання, «нічого» припустиме
void log(std::string_view);             // вид на символи
void total(std::span<const int>);       // вид на суцільні дані
void store(std::string);                // приймач-значення
void consume(Widget&&);                 // приймач нутрощів
void reseat(std::unique_ptr<Widget>&);  // перенацілення вказівника викликача
void adopt(std::unique_ptr<Widget>);    // забирає володіння цілком
void share(std::shared_ptr<Widget>);    // стає співвласником

void call_site() {
    Widget w;
    std::string s = "текст";
    std::vector<int> v{1, 2, 3};
    auto up = std::make_unique<Widget>();
    auto sp = std::make_shared<Widget>();

    inspect(w);                 // w лишається цілим і моїм
    tweak(w);                   // w змінено на місці
    inspect_opt(nullptr);       // законний аргумент, а не помилка

    log(s);                     // 2 слова, без копії й без виділення
    total(v);                   // вектор перетворюється у вид задарма

    store(s);                   // копія: s далі придатний
    store(std::move(s));        // переміщення: s спустошено, але живий
    consume(std::move(w));      // w спустошено; після цього рядка його не чіпаю

    reseat(up);                 // up дістає нове значення
    adopt(std::move(up));       // up == nullptr
    share(sp);                  // лічильник 1 → 2 на час виклику
}

#include <string>

std::string describe(const RequestState& st) {
    return std::visit(overloaded{
        [](const Loading&)      { return std::string{"Вантажимо…"}; },
        [](const Failed&  f)    { return "Помилка (" + std::to_string(f.httpCode)
                                         + "): " + f.message; },
        [](const Ready&   r)    { return "Готово, байтів: "
                                         + std::to_string(r.value.length); },
    }, st);
}

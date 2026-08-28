#include <iostream>
#include <string_view>

int main() {
    // Блок A: початковий фрагмент коду як незмінний строковий літерал
    constexpr std::string_view head = 
        "#include <iostream>\n"
        "#include <string_view>\n\n"
        "int main() {\n"
        "    constexpr std::string_view head = \n"
        "        ";

    // Хвостовий фрагмент коду, що містить логіку конструктора (Блок B)
    constexpr std::string_view tail = 
        ";\n"
        "    constexpr char q = '\"';\n"
        "    std::cout << head << q;\n"
        "    for (char c : head) {\n"
        "        if (c == '\\n') std::cout << \"\\n        \";\n"
        "        else if (c == '\"' || c == '\\\\') std::cout << '\\\\' << c;\n"
        "        else std::cout << c;\n"
        "    }\n"
        "    std::cout << q << tail;\n"
        "    return 0;\n"
        "}\n";

    constexpr char q = '"';

    // Блок B: відтворення повного тексту через послідовний вивід частин
    std::cout << head << q;
    for (char c : head) {
        if (c == '\n') std::cout << "\n        ";
        else if (c == '"' || c == '\\') std::cout << '\\' << c;
        else std::cout << c;
    }
    std::cout << q << tail;
    return 0;
}

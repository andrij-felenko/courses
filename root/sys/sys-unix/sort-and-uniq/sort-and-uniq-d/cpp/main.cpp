#include <iostream>
#include <string_view>
#include <locale>
#include <cstring>

int main() {
    std::string_view s1 = "abc-1";
    std::string_view s2 = "abc1";

    // 1. Стандартна UTF-8 локаль через std::locale
    try {
        std::locale utf8_loc("en_US.UTF-8");
        const auto& coll = std::use_facet<std::collate<char>>(utf8_loc);
        int res_utf8 = coll.compare(s1.data(), s1.data() + s1.size(),
                                    s2.data(), s2.data() + s2.size());
        std::cout << "en_US.UTF-8 collate: " << res_utf8 << '\n';
    } catch (const std::exception& e) {
        std::cerr << "Помилка завантаження локалі: " << e.what() << '\n';
    }

    // 2. Побайтове ASCII порівняння
    int res_c = std::strcmp(s1.data(), s2.data());
    std::cout << "C locale strcmp:     " << res_c << '\n';

    return 0;
}

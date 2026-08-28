#include <iostream>

int main() {
    std::string_view text = "banana";
    SuffixIndex index(text);

    std::cout << "=== Суфіксний індекс для тексту: \"" << text << "\" ===\n\n";
    std::cout << " k | SA[k] | LCP[k] | Суфікс тексту\n";
    std::cout << "---+-------+--------+-----------------\n";

    auto sa = index.get_sa();
    auto lcp = index.get_lcp();
    for (size_t i = 0; i < sa.size(); ++i) {
        std::cout << " " << i << " |   " << sa[i] << "   |   " << lcp[i] 
                  << "    | " << text.substr(sa[i]) << "\n";
    }

    auto repeated = index.longest_repeated_substring();
    std::cout << "\nНайдовший повторюваний підрядок: \"" << repeated 
              << "\" (довжина " << repeated.size() << ")\n";

    auto distinct = index.count_distinct_substrings();
    std::cout << "Кількість унікальних підрядків: " << distinct << " (очікувано 15)\n";

    int lcp_1_3 = index.query_lcp(1, 3);
    std::cout << "Швидкий запит LCP(SA[1], SA[3]) через Sparse Table: " 
              << lcp_1_3 << " (\"a\")\n";

    std::string_view query = "an";
    auto res = index.search(query);
    std::cout << "\nПошук зразка \"" << query << "\": знайдено " << res.count 
              << " входжень у діапазоні SA[" << res.left << ".." << res.right << "]:\n";
    if (res.found()) {
        for (int i = res.left; i <= res.right; ++i) {
            std::cout << "  -> зсув у тексті: " << sa[i] 
                      << " (підрядок \"" << text.substr(sa[i]) << "\")\n";
        }
    }

    return 0;
}

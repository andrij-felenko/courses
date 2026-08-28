#include <iostream>
#include <string>
#include <vector>
#include <cstdint>

// Структура для виконання пошуку Рабіна-Карпа
class RabinKarpMatcher {
private:
    static constexpr uint64_t B = 257;        // Основа полінома (більше за ASCII 255)
    static constexpr uint64_t P = 1000000007; // Просте число (модуль)

public:
    static std::vector<size_t> search(const std::string& text, const std::string& pattern) {
        std::vector<size_t> matches;
        size_t n = text.length();
        size_t m = pattern.length();

        if (m == 0 || n < m) {
            return matches;
        }

        // Обчислюємо E = (B^(m-1)) % P для старшого розряду
        uint64_t E = 1;
        for (size_t i = 0; i < m - 1; ++i) {
            E = (E * B) % P;
        }

        // Обчислюємо хеш шаблону та першого вікна тексту за схемою Горнера
        uint64_t hash_pattern = 0;
        uint64_t hash_text = 0;
        for (size_t i = 0; i < m; ++i) {
            hash_pattern = (hash_pattern * B + static_cast<uint8_t>(pattern[i])) % P;
            hash_text = (hash_text * B + static_cast<uint8_t>(text[i])) % P;
        }

        // Скануємо текст
        for (size_t i = 0; i <= n - m; ++i) {
            // При збігу хешів виконуємо посимвольну перевірку для захисту від колізій
            if (hash_text == hash_pattern) {
                bool is_match = true;
                for (size_t j = 0; j < m; ++j) {
                    if (text[i + j] != pattern[j]) {
                        is_match = false;
                        break;
                    }
                }
                if (is_match) {
                    matches.push_back(i);
                }
            }

            // Зсуваємо вікно праворуч на 1 символ (якщо є куди зсувати)
            if (i < n - m) {
                uint64_t leading_char = static_cast<uint8_t>(text[i]);
                uint64_t trailing_char = static_cast<uint8_t>(text[i + m]);

                // H' = (H_old - leading_char * E) % P
                uint64_t term = (leading_char * E) % P;
                uint64_t hash_sub = (hash_text >= term) ? (hash_text - term) : (hash_text + P - term);

                // H_new = (H' * B + trailing_char) % P
                hash_text = (hash_sub * B + trailing_char) % P;
            }
        }

        return matches;
    }
};

int main() {
    std::string text = "ABABDABACDABABCABAB";
    std::string pattern = "ABABCABAB";

    std::vector<size_t> matches = RabinKarpMatcher::search(text, pattern);

    std::cout << "Текст:   " << text << "\n";
    std::cout << "Шаблон:  " << pattern << "\n";
    std::cout << "Знайдено на індексах: ";
    for (size_t idx : matches) {
        std::cout << idx << " ";
    }
    std::cout << "\n";

    return 0;
}

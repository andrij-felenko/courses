#include "quoting.hpp"

namespace shexp {
namespace {

bool is_blank(char c) noexcept
{
    return c == ' ' || c == '\t' || c == '\n';
}

}  // namespace

std::size_t skip_quoted(std::string_view line, std::size_t i)
{
    const char c = line[i];

    if (c == '\\') {
        // Екран забирає рівно один наступний байт.
        return (i + 1 < line.size()) ? i + 2 : i + 1;
    }
    if (c == '\'') {
        // Усередині одинарних лапок екрана немає: навіть \' не рятує.
        const std::size_t close = line.find('\'', i + 1);
        return (close == std::string_view::npos) ? line.size() : close + 1;
    }
    if (c == '"') {
        std::size_t j = i + 1;
        while (j < line.size() && line[j] != '"') {
            j += (line[j] == '\\' && j + 1 < line.size()) ? 2 : 1;
        }
        return (j < line.size()) ? j + 1 : line.size();
    }
    return i + 1;
}

std::vector<std::string> split_words(std::string_view line)
{
    std::vector<std::string> words;

    for (std::size_t i = 0; i < line.size();) {
        while (i < line.size() && is_blank(line[i])) {
            ++i;
        }
        if (i >= line.size()) {
            break;
        }

        const std::size_t start = i;
        // Пробіл усередині лапок слова не ділить: skip_quoted перестрибує
        // весь захищений шматок цілком.
        while (i < line.size() && !is_blank(line[i])) {
            i = skip_quoted(line, i);
        }
        words.emplace_back(line.substr(start, i - start));
    }
    return words;
}

}  // namespace shexp

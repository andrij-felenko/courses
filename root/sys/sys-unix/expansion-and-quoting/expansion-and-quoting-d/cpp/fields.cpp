#include "fields.hpp"

namespace shexp {
namespace {

bool is_ws(char c) noexcept
{
    return c == ' ' || c == '\t' || c == '\n';
}

}  // namespace

std::vector<marked_word> split_fields(const marked_word& w, std::string_view ifs)
{
    const std::string_view text{w.text()};

    const auto delim = [&](std::size_t i) {
        const origin m = w.mark_at(i);
        return m.substituted && !m.quoted && ifs.find(text[i]) != std::string_view::npos;
    };
    // Білий простір IFS має окремі правила: його послідовності злипаються
    // в один роздільник, а на краях слова просто зникають.
    const auto delim_ws = [&](std::size_t i) { return delim(i) && is_ws(text[i]); };

    const auto slice = [&](std::size_t from, std::size_t to) {
        marked_word part;
        if (w.had_quotes()) {
            part.note_quotes();
        }
        for (std::size_t i = from; i < to; ++i) {
            part.append(text.substr(i, 1), w.mark_at(i));
        }
        return part;
    };

    std::vector<marked_word> out;

    // Порожній IFS вимикає фазу цілком: результат підстановки лишається
    // одним шматком, хай там хоч скільки пробілів.
    if (ifs.empty()) {
        out.push_back(slice(0, w.size()));
        return out;
    }

    if (w.size() == 0) {
        // Порожнє слово доживає до argv[] лише тоді, коли в записі були
        // лапки: "" це аргумент, а голий $EMPTY зникає безслідно.
        if (w.had_quotes()) {
            out.push_back(slice(0, 0));
        }
        return out;
    }

    std::size_t i = 0;
    while (i < w.size() && delim_ws(i)) {
        ++i;
    }

    while (i < w.size()) {
        const std::size_t start = i;
        while (i < w.size() && !delim(i)) {
            ++i;
        }
        out.push_back(slice(start, i));
        if (i >= w.size()) {
            break;
        }

        // Роздільник: білий простір, щонайбільше один небілий символ IFS,
        // знову білий простір. Дві сусідні коми лишають між собою порожнє
        // поле, а хвостовий роздільник зайвого слова не породжує.
        while (i < w.size() && delim_ws(i)) {
            ++i;
        }
        if (i < w.size() && delim(i)) {
            ++i;
            while (i < w.size() && delim_ws(i)) {
                ++i;
            }
        }
    }
    return out;
}

}  // namespace shexp

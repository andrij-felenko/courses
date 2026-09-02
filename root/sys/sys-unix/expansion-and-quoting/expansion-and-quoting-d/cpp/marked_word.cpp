#include "marked_word.hpp"

#include "expansion.hpp"

#include <cctype>
#include <cstdlib>
#include <optional>

#include <fnmatch.h>
#include <pwd.h>
#include <unistd.h>
#include <wordexp.h>   // заради кодів WRDE_* у expand_error

namespace shexp {

void marked_word::append(std::string_view bytes, origin mark)
{
    text_.append(bytes);
    marks_.insert(marks_.end(), bytes.size(), mark);
}

bool marked_word::has_active(std::string_view set) const
{
    for (std::size_t i = 0; i < text_.size(); ++i) {
        if (!marks_[i].quoted && set.find(text_[i]) != std::string_view::npos) {
            return true;
        }
    }
    return false;
}

std::string marked_word::glob_pattern() const
{
    constexpr std::string_view meta = "*?[]\\";

    std::string out;
    out.reserve(text_.size());
    for (std::size_t i = 0; i < text_.size(); ++i) {
        // Захищений метасимвол мусить дійти до glob(3) екранованим — інакше
        // зірочка з лапок раптом почала б шукати файли.
        if (marks_[i].quoted && meta.find(text_[i]) != std::string_view::npos) {
            out += '\\';
        }
        out += text_[i];
    }
    return out;
}

namespace {

constexpr std::size_t npos = std::string_view::npos;

std::size_t name_length(std::string_view s)
{
    const auto is_start = [](char c) {
        return std::isalpha(static_cast<unsigned char>(c)) != 0 || c == '_';
    };
    const auto is_body = [](char c) {
        return std::isalnum(static_cast<unsigned char>(c)) != 0 || c == '_';
    };

    if (s.empty() || !is_start(s.front())) {
        return 0;
    }
    std::size_t n = 1;
    while (n < s.size() && is_body(s[n])) {
        ++n;
    }
    return n;
}

std::optional<std::string> env_value(const std::string& name)
{
    if (const char* value = std::getenv(name.c_str())) {
        return std::string{value};
    }
    return std::nullopt;
}

// ${VAR#маска} і ${VAR##маска}. Маску зіставляє fnmatch(3) — той самий
// матчер, яким оболонка судить і імена файлів.
std::string trim_prefix(const std::string& value, const std::string& pattern, bool longest)
{
    std::size_t best = npos;
    for (std::size_t cut = 0; cut <= value.size(); ++cut) {
        if (::fnmatch(pattern.c_str(), value.substr(0, cut).c_str(), 0) == 0) {
            best = cut;
            if (!longest) {
                break;
            }
        }
    }
    return (best == npos) ? value : value.substr(best);
}

std::string trim_suffix(const std::string& value, const std::string& pattern, bool longest)
{
    std::size_t best = npos;
    for (std::size_t cut = 0; cut <= value.size(); ++cut) {
        if (::fnmatch(pattern.c_str(), value.substr(value.size() - cut).c_str(), 0) == 0) {
            best = cut;
            if (!longest) {
                break;
            }
        }
    }
    return (best == npos) ? value : value.substr(0, value.size() - best);
}

// Парна '}' усередині ${…}.
std::size_t brace_close(std::string_view s, std::size_t open)
{
    int depth = 0;
    for (std::size_t i = open; i < s.size(); ++i) {
        if (s[i] == '{') {
            ++depth;
        } else if (s[i] == '}' && --depth == 0) {
            return i;
        }
    }
    return npos;
}

// Розбирач одного слова. Стан — позиція в записі й слово, що росте;
// саме тому це клас, а не жменя функцій із наскрізним індексом.
class expander {
public:
    explicit expander(std::string_view raw) : raw_{raw} {}

    marked_word run();

private:
    void tilde();
    void dollar(origin base);
    void braced_parameter(origin base);
    void single_quotes();
    void double_quotes();

    std::string_view raw_;
    std::size_t i_ = 0;
    marked_word out_;
};

void expander::tilde()
{
    if (raw_.empty() || raw_.front() != '~') {
        return;
    }

    std::size_t end = 1;
    while (end < raw_.size() && raw_[end] != '/') {
        ++end;
    }

    std::optional<std::string> home;
    if (end == 1) {
        home = env_value("HOME");
        if (!home) {
            // $HOME може бути не задано — тоді питаємо системну базу
            // користувачів так само, як це робить оболонка.
            if (const passwd* pw = ::getpwuid(::getuid())) {
                home = std::string{pw->pw_dir};
            }
        }
    } else if (end == 2 && raw_[1] == '+') {
        home = env_value("PWD");
    } else if (end == 2 && raw_[1] == '-') {
        home = env_value("OLDPWD");
    } else {
        const std::string user{raw_.substr(1, end - 1)};
        if (const passwd* pw = ::getpwnam(user.c_str())) {
            home = std::string{pw->pw_dir};
        }
    }

    if (!home) {
        return;   // немає такої змінної чи користувача — тильда лишається текстом
    }
    // Результат тильди не ділять на слова й не глобять — позначаємо його
    // захищеним, хоч жодних лапок у записі не було.
    out_.append(*home, origin{true, false});
    i_ = end;
}

void expander::braced_parameter(origin base)
{
    const std::size_t close = brace_close(raw_, i_ + 1);
    if (close == npos) {
        throw expand_error{WRDE_SYNTAX, "незакрита конструкція ${…}"};
    }

    const std::string_view inner = raw_.substr(i_ + 2, close - i_ - 2);
    i_ = close + 1;

    const origin mark{base.quoted, true};

    if (inner.size() > 1 && inner.front() == '#') {
        // Рахуємо БАЙТИ; Bash у багатобайтній локалі рахує символи,
        // і на кирилиці числа розійдуться вдвічі.
        const auto value = env_value(std::string{inner.substr(1)});
        out_.append(std::to_string(value ? value->size() : 0U), mark);
        return;
    }

    const std::size_t n = name_length(inner);
    if (n == 0) {
        throw expand_error{WRDE_SYNTAX, "у ${…} немає імені параметра"};
    }

    std::string_view rest = inner.substr(n);
    bool colon = false;
    if (rest.size() >= 2 && rest[0] == ':'
        && std::string_view{"-=+?"}.find(rest[1]) != npos) {
        colon = true;
        rest.remove_prefix(1);
    }

    const char op = rest.empty() ? '\0' : rest.front();
    std::string_view arg = rest.empty() ? rest : rest.substr(1);
    bool longest = false;
    if ((op == '#' || op == '%') && !arg.empty() && arg.front() == op) {
        longest = true;
        arg.remove_prefix(1);
    }

    const std::string name{inner.substr(0, n)};
    const auto value = env_value(name);
    const bool unset = !value.has_value();
    // Двокрапка розширює перевірку з «не задано» на «не задано або порожнє».
    const bool missing = colon ? (unset || value->empty()) : unset;

    switch (op) {
    case '\0':
        out_.append(unset ? std::string{} : *value, mark);
        return;

    case '-':
        // Аргумент модифікатора сам проходить розгортання: ${A:-$B/типове}.
        out_.append(missing ? expand_word(arg).text() : *value, mark);
        return;

    case '=': {
        if (!missing) {
            out_.append(*value, mark);
            return;
        }
        // := не лише підставляє, а й присвоює — побічний ефект тут навмисний.
        const std::string produced = expand_word(arg).text();
        ::setenv(name.c_str(), produced.c_str(), 1);
        out_.append(produced, mark);
        return;
    }

    case '+':
        if (!missing) {
            out_.append(expand_word(arg).text(), mark);
        }
        return;

    case '?':
        if (missing) {
            throw expand_error{WRDE_BADVAL,
                               arg.empty() ? std::string{"параметр не задано"}
                                           : std::string{arg}};
        }
        out_.append(*value, mark);
        return;

    case '#':
        out_.append(trim_prefix(unset ? std::string{} : *value,
                                std::string{arg}, longest), mark);
        return;

    case '%':
        out_.append(trim_suffix(unset ? std::string{} : *value,
                                std::string{arg}, longest), mark);
        return;

    default:
        throw expand_error{WRDE_SYNTAX, "невідомий модифікатор у ${…}"};
    }
}

void expander::dollar(origin base)
{
    const char next = (i_ + 1 < raw_.size()) ? raw_[i_ + 1] : '\0';

    if (next == '(') {
        // І $(cmd), і $((expr)) свідомо лишаються за межами прикладу: перше
        // запускає процес, друге це окремий обчислювач виразів. Обидва
        // показує сусідній приклад на wordexp(3).
        throw expand_error{WRDE_CMDSUB, "підстановка команд і арифметика тут не виконуються"};
    }
    if (next == '{') {
        braced_parameter(base);
        return;
    }

    const std::size_t n = name_length(raw_.substr(i_ + 1));
    if (n == 0) {
        out_.append("$", base);   // долар без імені — звичайний символ
        ++i_;
        return;
    }

    const std::string name{raw_.substr(i_ + 1, n)};
    // Незадана змінна дає порожнечу, а не помилку: WRDE_UNDEF це вибір
    // того, хто кличе wordexp(3), а оболонка за замовчуванням мовчить.
    if (const auto value = env_value(name)) {
        out_.append(*value, origin{base.quoted, true});
    }
    i_ += 1 + n;
}

void expander::single_quotes()
{
    out_.note_quotes();
    const std::size_t close = raw_.find('\'', i_ + 1);
    if (close == npos) {
        throw expand_error{WRDE_SYNTAX, "незакрита одинарна лапка"};
    }
    // Найжорсткіший захист: усе між лапками — буквальний текст.
    out_.append(raw_.substr(i_ + 1, close - i_ - 1), origin{true, false});
    i_ = close + 1;
}

void expander::double_quotes()
{
    out_.note_quotes();
    ++i_;

    while (i_ < raw_.size()) {
        if (raw_[i_] == '"') {
            ++i_;
            return;
        }
        if (raw_[i_] == '\\' && i_ + 1 < raw_.size()
            && std::string_view{"$`\"\\"}.find(raw_[i_ + 1]) != npos) {
            // У подвійних лапках слеш екранує лише ці чотири символи;
            // перед рештою він сам лишається буквальним.
            out_.append(raw_.substr(i_ + 1, 1), origin{true, false});
            i_ += 2;
        } else if (raw_[i_] == '$') {
            dollar(origin{true, false});
        } else {
            out_.append(raw_.substr(i_, 1), origin{true, false});
            ++i_;
        }
    }
    throw expand_error{WRDE_SYNTAX, "незакрита подвійна лапка"};
}

marked_word expander::run()
{
    tilde();   // фаза 2: тильда діє лише на самому початку слова

    while (i_ < raw_.size()) {
        const char c = raw_[i_];

        if (c == '\\') {
            if (i_ + 1 < raw_.size()) {
                out_.append(raw_.substr(i_ + 1, 1), origin{true, false});
                i_ += 2;
            } else {
                out_.append("\\", origin{});
                ++i_;
            }
        } else if (c == '\'') {
            single_quotes();
        } else if (c == '"') {
            double_quotes();
        } else if (c == '$') {
            dollar(origin{});
        } else {
            out_.append(raw_.substr(i_, 1), origin{});
            ++i_;
        }
    }
    return std::move(out_);
}

}  // namespace

marked_word expand_word(std::string_view raw)
{
    expander one{raw};
    return one.run();
}

}  // namespace shexp

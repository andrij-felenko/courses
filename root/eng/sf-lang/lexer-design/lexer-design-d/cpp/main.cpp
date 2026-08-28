#include <cctype>
#include <string>
#include <string_view>

enum class Kind { Num, Ident, Plus, Minus,
                  Star, LParen, RParen, End };

struct Token {
    Kind        kind  = Kind::End;
    int         value = 0;     // для Num — розібране число
    std::string text;          // для Ident — саме ім'я (лексема)
};

class Lexer {
    std::string_view src_;
    size_t           pos_ = 0;   // поточна позиція у вхідному тексті

    char peek() const { return pos_ < src_.size() ? src_[pos_] : '\0'; }

public:
    explicit Lexer(std::string_view src) : src_(src) {}

    Token next() {
        while (std::isspace((unsigned char)peek()))   // 1) проковтнути пробіли
            ++pos_;

        if (peek() == '\0')                           // кінець вводу
            return { Kind::End };

        if (std::isdigit((unsigned char)peek())) {    // 2) НАЙДОВШЕ число
            int v = 0;
            while (std::isdigit((unsigned char)peek()))   // тягнемо цифри, доки йдуть
                v = v * 10 + (src_[pos_++] - '0');        // тут-таки рахуємо значення
            return { Kind::Num, v };
        }

        if (std::isalpha((unsigned char)peek())) {    // 3) НАЙДОВШЕ ім'я
            std::string text;
            while (std::isalnum((unsigned char)peek()))
                text += src_[pos_++];                 // тягнемо буквоцифри
            return { Kind::Ident, 0, std::move(text) };  // (ключові слова — нижче)
        }

        switch (src_[pos_++]) {                       // 4) односимвольні оператори й дужки
            case '+': return { Kind::Plus };
            case '-': return { Kind::Minus };
            case '*': return { Kind::Star };
            case '(': return { Kind::LParen };
            case ')': return { Kind::RParen };
            default:  return { Kind::End };            // невідомий символ — тут спрощено
        }
    }
};

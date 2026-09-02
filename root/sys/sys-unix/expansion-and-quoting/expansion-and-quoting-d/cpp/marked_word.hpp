// marked_word.hpp — слово разом із маскою походження кожного байта.
//
// Лапки в текст слова не потрапляють узагалі: замість них кожен байт несе
// позначку, чи був він захищений. Інакше після фази 6 зірочку з лапок не
// відрізнити від живої маски — а вирішувати це доводиться пізніше, аж на
// фазі глобінгу. Оболонка робить так само: тримає службові позначки поруч
// із текстом до самого кінця конвеєра.
#pragma once

#include <cstddef>
#include <string>
#include <string_view>
#include <vector>

namespace shexp {

// Звідки взявся байт. Від цього залежить, чи дійде він до фази 4 живим
// роздільником і до фази 5 живим метасимволом.
struct origin {
    bool quoted = false;       // був у лапках або за зворотним слешем
    bool substituted = false;  // прийшов з розгортання, а не набраний руками
};

class marked_word {
public:
    void append(std::string_view bytes, origin mark);
    void note_quotes() noexcept { had_quotes_ = true; }

    [[nodiscard]] const std::string& text() const noexcept { return text_; }
    [[nodiscard]] std::size_t size() const noexcept { return text_.size(); }
    [[nodiscard]] origin mark_at(std::size_t i) const { return marks_[i]; }

    // У записі були лапки — навіть якщо порожні.
    [[nodiscard]] bool had_quotes() const noexcept { return had_quotes_; }

    // Чи лишився в слові живий (незахищений) байт із набору.
    [[nodiscard]] bool has_active(std::string_view set) const;

    // Рядок для glob(3): захищені метасимволи екрановано зворотним слешем.
    [[nodiscard]] std::string glob_pattern() const;

private:
    std::string text_;
    std::vector<origin> marks_;
    bool had_quotes_ = false;
};

// Фази 2, 3 і 6: тильда, параметри з оточення, зняття лапок.
// Кидає expand_error на незакриті лапки, на $(…) і на ${VAR:?…}.
[[nodiscard]] marked_word expand_word(std::string_view raw);

}  // namespace shexp

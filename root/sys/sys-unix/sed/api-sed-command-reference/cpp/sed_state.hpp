// sed_state.hpp — Pattern Space і Hold Space як std::string.
//
// std::string сам тримає термінатор за останнім байтом і сам росте геометрично,
// тож увесь ручний realloc із C-версії тут просто зникає: лишається семантика
// регістрових команд sed, і нічого більше.
#pragma once

#include <cstddef>
#include <istream>
#include <ostream>
#include <string>
#include <string_view>

namespace minised {

class SedState {
public:
    [[nodiscard]] std::string& pattern() noexcept { return pattern_; }
    [[nodiscard]] const std::string& pattern() const noexcept { return pattern_; }
    [[nodiscard]] const std::string& hold() const noexcept { return hold_; }
    [[nodiscard]] std::size_t line_number() const noexcept { return line_; }
    [[nodiscard]] bool last_line() const noexcept { return last_; }   // адреса $
    [[nodiscard]] bool deleted() const noexcept { return deleted_; }
    [[nodiscard]] bool subst_success() const noexcept { return subst_ok_; }
    void set_subst_success(bool ok) noexcept { subst_ok_ = ok; }      // брудний біт для t/T
    void reset_counters() noexcept { line_ = 0; last_ = false; deleted_ = false; }

    void hold_copy() { hold_ = pattern_; }                            // h
    // На старті Hold Space порожній, тож перше H дає провідний '\n' —
    // звідси ідіома 1h; 1!H у скриптах.
    void hold_append() { hold_ += '\n'; hold_ += pattern_; }          // H
    void get_copy() { pattern_ = hold_; }                             // g
    void get_append() { pattern_ += '\n'; pattern_ += hold_; }        // G
    void exchange() noexcept { pattern_.swap(hold_); }                // x — строго O(1)
    void zap() noexcept { pattern_.clear(); }                         // z — ємність лишається
    void erase() noexcept { pattern_.clear(); deleted_ = true; }      // d

    // D: true — сценарій перезапускається над залишком БЕЗ читання нового запису.
    bool delete_first_line() {
        const auto nl = pattern_.find('\n');
        if (nl == std::string::npos) {
            erase();
            return false;
        }
        pattern_.erase(0, nl + 1);
        return true;
    }

    void print(std::ostream& os, char sep = '\n') const {             // p
        os.write(pattern_.data(), static_cast<std::streamsize>(pattern_.size()));
        os.put(sep);
    }

    void print_first_line(std::ostream& os, char sep = '\n') const {  // P
        const auto nl = pattern_.find('\n');
        const std::string_view head{pattern_.data(),
                                    nl == std::string::npos ? pattern_.size() : nl};
        os.write(head.data(), static_cast<std::streamsize>(head.size()));
        os.put(sep);
    }

    // Роздільник у Pattern Space не потрапляє: через це '$' у регулярному виразі
    // зіставляється з кінцем тексту, а не з переносом рядка.
    bool read_record(std::istream& in, char sep = '\n') {
        deleted_ = false;
        subst_ok_ = false;
        if (!std::getline(in, pattern_, sep)) return false;
        ++line_;
        last_ = (in.peek() == std::char_traits<char>::eof());
        return true;
    }

private:
    std::string pattern_;
    std::string hold_;
    std::size_t line_{0};
    bool last_{false};
    bool deleted_{false};
    bool subst_ok_{false};
};

}  // namespace minised

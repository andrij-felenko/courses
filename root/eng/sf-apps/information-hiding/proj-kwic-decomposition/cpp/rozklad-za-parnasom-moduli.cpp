#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <algorithm>

/* МОДУЛЬ 1: Сховище рядків (Інкапсулює спосіб зберігання) */
class LineStorage {
public:
    void add_line(std::string_view line) {
        offsets_.push_back(buffer_.size());
        lengths_.push_back(line.size());
        buffer_.append(line);
    }

    [[nodiscard]] size_t line_count() const noexcept { return offsets_.size(); }
    [[nodiscard]] size_t line_length(size_t line_idx) const noexcept { return lengths_[line_idx]; }

    [[nodiscard]] char get_char(size_t line_idx, size_t char_idx) const noexcept {
        if (line_idx >= offsets_.size() || char_idx >= lengths_[line_idx]) return '\0';
        return buffer_[offsets_[line_idx] + char_idx];
    }

private:
    std::string buffer_;
    std::vector<size_t> offsets_;
    std::vector<size_t> lengths_;
};

/* МОДУЛЬ 2: Циклічні зсуви (Інкапсулює віртуальне зміщення слів) */
class CircularShifts {
public:
    explicit CircularShifts(const LineStorage &storage) : storage_(storage) {
        for (size_t l = 0; l < storage_.line_count(); ++l) {
            size_t len = storage_.line_length(l);
            bool in_word = false;
            for (size_t c = 0; c < len; ++c) {
                char ch = storage_.get_char(l, c);
                if (ch != ' ' && !in_word) {
                    in_word = true;
                    shifts_.push_back({l, c});
                } else if (ch == ' ') {
                    in_word = false;
                }
            }
        }
    }

    [[nodiscard]] size_t count() const noexcept { return shifts_.size(); }

    [[nodiscard]] char get_char(size_t shift_idx, size_t pos) const noexcept {
        const auto &s = shifts_[shift_idx];
        size_t len = storage_.line_length(s.line_index);
        if (pos >= len) return '\0';
        
        size_t mapped = (s.word_start_char + pos) % (len + 1);
        if (mapped == len) return ' ';
        return storage_.get_char(s.line_index, mapped);
    }

private:
    struct ShiftRef {
        size_t line_index;
        size_t word_start_char;
    };
    const LineStorage &storage_;
    std::vector<ShiftRef> shifts_;
};

/* МОДУЛЬ 3: Упорядкування (Інкапсулює алгоритм сортування) */
class Alphabetizer {
public:
    explicit Alphabetizer(const CircularShifts &shifts) : shifts_(shifts) {
        order_.resize(shifts_.count());
        for (size_t i = 0; i < order_.size(); ++i) order_[i] = i;

        std::sort(order_.begin(), order_.end(), [this](size_t a, size_t b) {
            size_t p = 0;
            while (true) {
                char ca = shifts_.get_char(a, p);
                char cb = shifts_.get_char(b, p);
                if (ca != cb) return ca < cb;
                if (ca == '\0') return false;
                ++p;
            }
        });
    }

    [[nodiscard]] size_t sorted_shift_index(size_t rank) const noexcept {
        return order_[rank];
    }

private:
    const CircularShifts &shifts_;
    std::vector<size_t> order_;
};

/* МОДУЛЬ 4: Вивід */
class OutputFormatter {
public:
    static void print(const Alphabetizer &alpha, const CircularShifts &shifts) {
        for (size_t i = 0; i < shifts.count(); ++i) {
            size_t s_idx = alpha.sorted_shift_index(i);
            size_t pos = 0;
            while (true) {
                char c = shifts.get_char(s_idx, pos++);
                if (c == '\0') break;
                std::cout << c;
            }
            std::cout << '\n';
        }
    }
};

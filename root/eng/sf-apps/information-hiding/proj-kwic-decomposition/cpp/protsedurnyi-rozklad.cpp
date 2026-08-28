#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>

/* СПІЛЬНА СТРУКТУРА: виставляє представлення масиву й зсувів */
struct SharedKwicData {
    std::string raw_chars;
    std::vector<size_t> line_offsets;
    
    struct ShiftEntry {
        size_t line_index;
        size_t char_offset_in_line;
    };
    std::vector<ShiftEntry> shifts;
};

/* Модуль 1: Ввід */
void step_input(SharedKwicData &data, const std::vector<std::string> &lines) {
    data.raw_chars.clear();
    data.line_offsets.clear();
    for (const auto &ln : lines) {
        data.line_offsets.push_back(data.raw_chars.size());
        data.raw_chars.append(ln);
        data.raw_chars.push_back('\0');
    }
}

/* Модуль 2: Циклічний зсув */
void step_circular_shift(SharedKwicData &data) {
    data.shifts.clear();
    for (size_t l = 0; l < data.line_offsets.size(); ++l) {
        const char *line = &data.raw_chars[data.line_offsets[l]];
        size_t offset = 0;
        bool in_word = false;
        
        while (line[offset] != '\0') {
            if (line[offset] != ' ' && !in_word) {
                in_word = true;
                data.shifts.push_back({l, offset});
            } else if (line[offset] == ' ') {
                in_word = false;
            }
            ++offset;
        }
    }
}

/* Модуль 3: Сортування */
std::vector<size_t> step_alphabetize(const SharedKwicData &data) {
    std::vector<size_t> order(data.shifts.size());
    for (size_t i = 0; i < order.size(); ++i) order[i] = i;
    
    std::sort(order.begin(), order.end(), [&](size_t a, size_t b) {
        const auto &sa = data.shifts[a];
        const auto &sb = data.shifts[b];
        const char *line_a = &data.raw_chars[data.line_offsets[sa.line_index]];
        const char *line_b = &data.raw_chars[data.line_offsets[sb.line_index]];
        std::string_view va(line_a + sa.char_offset_in_line);
        std::string_view vb(line_b + sb.char_offset_in_line);
        return va < vb;
    });
    return order;
}

/* Модуль 4: Вивід */
void step_output(const SharedKwicData &data, const std::vector<size_t> &order) {
    for (size_t idx : order) {
        const auto &s = data.shifts[idx];
        const char *line = &data.raw_chars[data.line_offsets[s.line_index]];
        std::string_view suffix(line + s.char_offset_in_line);
        std::cout << suffix;
        if (s.char_offset_in_line > 0) {
            std::string_view prefix(line, s.char_offset_in_line);
            std::cout << " / " << prefix;
        }
        std::cout << '\n';
    }
}

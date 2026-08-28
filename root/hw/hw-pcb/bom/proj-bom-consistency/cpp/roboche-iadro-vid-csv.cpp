#include <cstdio>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>

// Розбити ОДИН рядок CSV на поля за правилами RFC 4180:
//  - кома РОЗДІЛЯЄ поля ТІЛЬКИ поза лапками;
//  - поле в лапках може містити коми (вони — частина значення);
//  - подвоєна лапка "" усередині лапок означає одну літеральну лапку.
static std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::string cur;
    bool in_quotes = false;
    for (size_t i = 0; i < line.size(); ++i) {
        char c = line[i];
        if (in_quotes) {
            if (c == '"') {
                if (i + 1 < line.size() && line[i + 1] == '"') {  // "" → одна лапка
                    cur.push_back('"');
                    ++i;                                          // проковтнути другу
                } else {
                    in_quotes = false;                            // кінець поля в лапках
                }
            } else {
                cur.push_back(c);                                 // звичайний символ усередині лапок
            }
        } else {
            if (c == '"') {
                in_quotes = true;                                 // початок поля в лапках
            } else if (c == ',') {
                fields.push_back(cur);                            // кома ПОЗА лапками — роздільник
                cur.clear();
            } else {
                cur.push_back(c);
            }
        }
    }
    fields.push_back(cur);                                        // останнє поле
    return fields;
}

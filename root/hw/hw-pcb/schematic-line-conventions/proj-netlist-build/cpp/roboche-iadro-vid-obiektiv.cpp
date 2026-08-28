#include <cstdint>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>

// Точка на аркуші — у КРОКАХ СІТКИ (цілі!), щоб «дотик» був точним ==, а не «майже».
struct Point {
    int32_t x, y;
    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
};
struct PointHash {                       // щоб Point міг бути ключем у хеш-таблиці
    size_t operator()(const Point& p) const {
        return (uint64_t(uint32_t(p.x)) << 32) ^ uint32_t(p.y);
    }
};

struct Wire { Point a, b; };             // відрізок дроту: два кінці
struct Pin  { Point at; int part, num; std::string name; };  // вивід деталі

// Мітка ланцюга. scope розрізняє радіус дії: локальна діє в межах аркуша,
// глобальна — по всьому проєкту. Тому ключ збігу — ПАРА (ім'я, область).
enum class Scope { Local, Global };
struct Label { Point at; std::string name; Scope scope; int sheet; };

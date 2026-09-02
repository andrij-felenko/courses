// array.hpp — асоціативний масив AWK у C++.
//
// Пара до c/internals/array_layout.h, але ланцюжки колізій і рехешування тут
// не пишуться руками: це вже є в std::unordered_map, причому з тими самими
// гарантіями (окремі ланцюжки, амортизована O(1) вставка, поріг за
// коефіцієнтом завантаження). Що НЕ віддається бібліотеці — вибір хеш-функції
// та семантика AWK: автоініціалізація, оператор in, дві форми delete й
// складені ключі через SUBSEP.
#pragma once

#include <algorithm>
#include <cstddef>
#include <functional>
#include <initializer_list>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

#include "node.hpp"

namespace awk::internals {

// ASCII 0x1C (Unit Separator): у друкованому тексті не трапляється, тому
// склеєні ним ключі майже не мають шансів на колізію з реальними даними.
inline constexpr char kSubsepDefault[] = "\034";

// Хеш Пітера Вайнбергера (PJW/ElfHash) — те саме сімейство, що й у gawk за
// замовчуванням. std::hash<std::string> тут теж працював би; власний функтор
// лишено навмисно, бо в C++ вибір хеш-функції — це ПАРАМЕТР контейнера, а не
// правка його нутрощів, як довелося б у C.
struct PjwHash {
    [[nodiscard]] std::size_t operator()(const std::string &key) const noexcept
    {
        unsigned long h = 0;
        for (const unsigned char c : key) {
            h = (h << 4) + c;
            if (const unsigned long g = h & 0xf0000000UL) {
                h ^= g >> 24;
                h ^= g;
            }
        }
        return static_cast<std::size_t>(h);
    }
};

// Значення PROCINFO["sorted_in"], які має сенс моделювати.
enum class Order {
    Unsorted,      // сирий порядок хеш-таблиці: найшвидший і найменш стабільний
    IndexStrAsc,
    IndexStrDesc,
    IndexNumAsc,
    IndexNumDesc,
    ValueStrAsc,
    ValueNumAsc,
    ValueNumDesc
};

class Array {
public:
    // Читання неіснуючого елемента в AWK його СТВОРЮЄ, і operator[] у
    // std::unordered_map поводиться так само. Збіг не випадковий: обидва
    // повертають посилання на комірку, а щоб було на що посилатися, комірку
    // доводиться завести.
    [[nodiscard]] Node &lookup(const std::string &key) { return map_[key]; }

    // Оператор in: перевіряє й НЕ створює. Уся різниця між акуратним
    // скриптом і масивом розміром із вхідний файл — у цих двох рядках.
    [[nodiscard]] bool contains(const std::string &key) const
    {
        return map_.find(key) != map_.end();
    }

    // Пошук без автоініціалізації: nullptr замість створеної комірки.
    [[nodiscard]] Node *find(const std::string &key)
    {
        const auto it = map_.find(key);
        return it == map_.end() ? nullptr : &it->second;
    }

    // delete arr[k]. Розмір масиву відер при цьому не зменшується — так само,
    // як у інтерпретаторі.
    bool erase(const std::string &key) { return map_.erase(key) != 0; }

    // delete arr: за один прохід гинуть і вузли, і сама таблиця відер.
    // Без rehash(0) відра лишилися б розтягнутими на попередній пік, і
    // циклічна обробка пакетів тримала б цю пам'ять до кінця процесу.
    void clear()
    {
        map_.clear();
        map_.rehash(0);
    }

    [[nodiscard]] std::size_t size() const noexcept { return map_.size(); }
    [[nodiscard]] bool empty() const noexcept { return map_.empty(); }
    [[nodiscard]] std::size_t bucket_count() const noexcept { return map_.bucket_count(); }
    [[nodiscard]] float load_factor() const noexcept { return map_.load_factor(); }

    // arr[i, j] — не двовимірність, а склейка в один рядковий ключ.
    [[nodiscard]] static std::string subsep_key(std::initializer_list<std::string_view> parts,
                                                std::string_view subsep = kSubsepDefault)
    {
        std::string key;
        std::size_t total = 0;
        for (const auto part : parts)
            total += part.size() + subsep.size();
        key.reserve(total);

        bool first = true;
        for (const auto part : parts) {
            if (!first)
                key.append(subsep);
            key.append(part);
            first = false;
        }
        return key;
    }

    // Зворотна операція — те, що в AWK робить split(k, parts, SUBSEP).
    [[nodiscard]] static std::vector<std::string> split_key(const std::string &key,
                                                            std::string_view subsep = kSubsepDefault)
    {
        std::vector<std::string> parts;
        if (subsep.empty()) {
            parts.push_back(key);
            return parts;
        }

        std::size_t from = 0;
        for (;;) {
            const std::size_t at = key.find(subsep, from);
            if (at == std::string::npos) {
                parts.emplace_back(key, from);
                return parts;
            }
            parts.emplace_back(key, from, at - from);
            from = at + subsep.size();
        }
    }

    // Порядок обходу for (k in arr). Метод не const, бо сортування за
    // значеннями змушує комірки виробити числову або рядкову форму — а це
    // запис у кеш.
    [[nodiscard]] std::vector<std::string> keys(Order order = Order::Unsorted)
    {
        std::vector<std::string> out;
        out.reserve(map_.size());
        for (const auto &entry : map_)
            out.push_back(entry.first);

        switch (order) {
        case Order::Unsorted:
            break;
        case Order::IndexStrAsc:
            std::sort(out.begin(), out.end());
            break;
        case Order::IndexStrDesc:
            std::sort(out.begin(), out.end(), std::greater<>());
            break;
        case Order::IndexNumAsc:
            sort_by_index_number(out, true);
            break;
        case Order::IndexNumDesc:
            sort_by_index_number(out, false);
            break;
        case Order::ValueStrAsc:
            std::sort(out.begin(), out.end(), [this](const auto &a, const auto &b) {
                return map_[a].as_string() < map_[b].as_string();
            });
            break;
        case Order::ValueNumAsc:
            sort_by_value_number(out, true);
            break;
        case Order::ValueNumDesc:
            sort_by_value_number(out, false);
            break;
        }
        return out;
    }

private:
    void sort_by_index_number(std::vector<std::string> &keys, bool ascending)
    {
        // Ключ масиву завжди рядок, навіть коли він "42": числове
        // впорядкування — це перетворення на льоту, а не інший тип ключа.
        std::sort(keys.begin(), keys.end(), [ascending](const auto &a, const auto &b) {
            const double x = parse_prefix(a);
            const double y = parse_prefix(b);
            return ascending ? x < y : y < x;
        });
    }

    void sort_by_value_number(std::vector<std::string> &keys, bool ascending)
    {
        std::sort(keys.begin(), keys.end(), [this, ascending](const auto &a, const auto &b) {
            const double x = map_[a].as_number();
            const double y = map_[b].as_number();
            return ascending ? x < y : y < x;
        });
    }

    // Гетерогенного пошуку (find за string_view без побудови рядка) для
    // невпорядкованих контейнерів немає до C++20, тому ключі приймаються
    // як std::string. Це чесна ціна вибору стандарту, а не недогляд.
    std::unordered_map<std::string, Node, PjwHash> map_;
};

} // namespace awk::internals

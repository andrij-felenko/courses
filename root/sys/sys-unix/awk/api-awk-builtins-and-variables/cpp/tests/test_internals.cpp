// test_internals.cpp — перевірка моделей із cpp/internals та хешу FNV-1a.
//
// Збірка й запуск (gawk і його заголовки НЕ потрібні — саме заради цього
// моделі й не підключають <gawkapi.h>):
//   c++ -std=c++17 -Wall -Wextra -O2 -o test_internals tests/test_internals.cpp
//   ./test_internals
//
// Тести перевіряють рівно те, що обіцяє довідник: матрицю порівнянь POSIX,
// правила перетворення типів, автоініціалізацію елементів масиву й склейку
// складених ключів через SUBSEP.
#include <cstdio>
#include <string>
#include <vector>

#include "../fnv1a.hpp"
#include "../internals/array.hpp"
#include "../internals/node.hpp"

namespace {

int failures = 0;
int checks = 0;

void check(bool condition, const char *what)
{
    ++checks;
    if (!condition) {
        ++failures;
        std::printf("  ✖ %s\n", what);
    }
}

template <typename T>
void check_eq(const T &got, const T &want, const char *what)
{
    ++checks;
    if (!(got == want)) {
        ++failures;
        std::printf("  ✖ %s\n", what);
    }
}

using namespace awk::internals;

void test_fnv1a()
{
    std::printf("FNV-1a\n");
    // Канонічні вектори алгоритму: якщо зійшлися вони, зійдеться все інше.
    check(fast_tools::fnv1a_64("") == 0xcbf29ce484222325ULL, "порожній вхід дає базис");
    check(fast_tools::fnv1a_64("a") == 0xaf63dc4c8601ec8cULL, "хеш \"a\"");
    check(fast_tools::fnv1a_64("foobar") == 0x85944171f73967e8ULL, "хеш \"foobar\"");

    // Байт зі старшим бітом не повинен розповзтися одиницями: char знаковий.
    check(fast_tools::fnv1a_64("\x80") != fast_tools::fnv1a_64("\xff"),
          "старший біт оброблено як беззнаковий байт");

    const auto hex = fast_tools::to_hex(0xcbf29ce484222325ULL);
    check_eq(std::string(hex.data(), hex.size()), std::string("0xcbf29ce484222325"),
             "шістнадцятковий запис хешу");

    const auto zero = fast_tools::to_hex(0);
    check_eq(std::string(zero.data(), zero.size()), std::string("0x0000000000000000"),
             "нуль друкується шістнадцятьма нулями");

    // Секціонування: 20 000 ключів мусять покрити всі 64 партиції, інакше
    // Grace-join отримав би перекіс уже на етапі розбиття.
    std::vector<int> hits(64, 0);
    for (int i = 0; i < 20000; ++i)
        ++hits[fast_tools::partition_of("10.0.0." + std::to_string(i), 64)];
    bool all_used = true;
    for (const int n : hits)
        if (n == 0) all_used = false;
    check(all_used, "усі партиції отримали ключі");
}

void test_comparison_matrix()
{
    std::printf("матриця порівнянь POSIX\n");

    Node input_010 = Node::from_input("010");
    Node input_10  = Node::from_input("10");
    Node text_010  = Node::from_string("010");
    Node text_10   = Node::from_string("10");
    Node text_10_0 = Node::from_string("10.0");
    Node num_10    = Node::from_number(10);
    Node empty;

    check(input_010.is_strnum(), "поле з вводу \"010\" — це strnum");
    check(!text_010.is_strnum(), "літерал \"010\" strnum-ом не є");

    check(equals(input_010, input_10), "strnum проти strnum — числове");
    check(!equals(text_010, text_10), "рядок проти рядка — лексикографічне");
    check(compare(text_010, text_10) == Ordering::Less, "\"010\" < \"10\" побайтово");

    check(equals(input_010, text_010), "strnum проти рядка — рядкове, тексти збіглися");
    check(!equals(input_010, text_10), "strnum проти рядка — рядкове, тексти різні");

    check(equals(input_010, num_10), "strnum проти числа — числове");

    // Критична пастка POSIX: число проти рядка порівнюється ЯК РЯДОК.
    check(equals(num_10, text_10), "10 == \"10\": CONVFMT дав \"10\"");
    check(!equals(num_10, text_10_0), "10 != \"10.0\": порівняно тексти, не числа");
    Node text_9 = Node::from_string("9");
    check(compare(num_10, text_9) == Ordering::Less, "10 < \"9\" — теж рядкове");

    // Рядок із хвостом числовим рядком не є.
    Node mb = Node::from_input("100MB");
    Node num_100 = Node::from_number(100);
    check(!mb.is_strnum(), "\"100MB\" не strnum");
    check(!equals(mb, num_100), "\"100MB\" != 100");
    check(mb.as_number() == 100.0, "але префіксне перетворення дає 100");

    // Провідний плюс і пробіли навколо числа синтаксису не псують.
    Node padded = Node::from_input("  +7 ");
    check(padded.is_strnum(), "\"  +7 \" — числовий рядок");
    Node num_7 = Node::from_number(7);
    check(equals(padded, num_7), "  +7  == 7 числово");

    // Неініціалізована змінна — і 0, і "" водночас.
    Node zero = Node::from_number(0);
    Node blank = Node::from_string("");
    Node other;
    check(equals(empty, zero), "неініціалізована == 0");
    check(equals(empty, blank), "неініціалізована == \"\"");
    check(equals(empty, other), "дві неініціалізовані рівні");

    // Мутація вбиває strnum: після конкатенації поле стає звичайним рядком.
    Node mutated = Node::from_input("010");
    mutated.assign_string("010");
    check(!mutated.is_strnum(), "після присвоєння рядка strnum зникає");
    check(!equals(mutated, input_10), "і порівняння стало рядковим");

    // Розходження з gawk, зафіксоване в коментарі до is_strnum().
    Node blank_field = Node::from_input("");
    check(!blank_field.is_strnum(), "порожнє поле в цій моделі не strnum");
}

void test_conversions()
{
    std::printf("перетворення типів\n");

    Node million = Node::from_number(1000000);
    check_eq(million.as_string(), std::string("1000000"), "ціле не стає \"1e+06\"");

    Node pi = Node::from_number(3.14159265);
    check_eq(pi.as_string("%.6g"), std::string("3.14159"), "CONVFMT за замовчуванням");

    Node pi2 = Node::from_number(3.14159265);
    check_eq(pi2.as_string("%.2g"), std::string("3.1"), "CONVFMT %.2g");

    // Кеш працює в обидва боки й переживає повторні звертання.
    Node field = Node::from_input("42");
    check(!field.has_number_cache(), "до арифметики strtod не викликано");
    check(field.as_number() == 42.0, "перше звертання рахує");
    check(field.has_number_cache(), "друге бере з кешу");
    check_eq(field.as_string(), std::string("42"), "рядкова форма — оригінальний текст");

    Node junk = Node::from_input("error 404");
    check(junk.as_number() == 0.0, "нечисловий рядок дає 0");

    Node hex = Node::from_input("0x1F");
    check(hex.as_number() == 0.0, "\"0x1F\" + 0 — це 0, а не 31");

    Node inf = Node::from_input("inf");
    check(!inf.is_strnum(), "\"inf\" числовим рядком не вважається");
}

void test_array()
{
    std::printf("асоціативний масив\n");

    Array cache;
    check(cache.empty(), "новий масив порожній");

    check(!cache.contains("ghost"), "in не знаходить неіснуючий ключ");
    check_eq(cache.size(), std::size_t{0}, "in нічого не створив");
    check(cache.find("ghost") == nullptr, "find теж не створює");
    check_eq(cache.size(), std::size_t{0}, "масив досі порожній");

    // А от читання — створює.
    (void) cache.lookup("ghost").as_string();
    check_eq(cache.size(), std::size_t{1}, "читання завело комірку");
    check(cache.contains("ghost"), "ключ тепер існує");

    check(cache.erase("ghost"), "delete arr[k] прибрав ключ");
    check(!cache.erase("ghost"), "повторне видалення нічого не знаходить");
    check_eq(cache.size(), std::size_t{0}, "масив знову порожній");

    // Ціна недбалої перевірки на масштабі.
    Array careless;
    Array careful;
    for (int i = 0; i < 5000; ++i) {
        const std::string key = "10.0.0." + std::to_string(i);
        if (careless.lookup(key).as_string().empty())
            (void) 0;
        if (!careful.contains(key))
            (void) 0;
    }
    check_eq(careless.size(), std::size_t{5000}, "недбала перевірка роздула масив");
    check_eq(careful.size(), std::size_t{0}, "акуратна лишила його порожнім");

    const std::size_t grown = careless.bucket_count();
    careless.clear();
    check_eq(careless.size(), std::size_t{0}, "delete arr спорожнив таблицю");
    check(careless.bucket_count() < grown, "і відра стиснулися назад");

    // Складені ключі.
    Array stat;
    stat.lookup(Array::subsep_key({"web", "500"})).assign_number(12);
    stat.lookup(Array::subsep_key({"db", "500"})).assign_number(3);
    check_eq(stat.size(), std::size_t{2}, "два складені ключі");
    check(stat.contains(Array::subsep_key({"web", "500"})), "складений ключ знаходиться");
    check(!stat.contains(Array::subsep_key({"api", "500"})), "чужого немає");
    check_eq(stat.size(), std::size_t{2}, "перевірка масив не виростила");

    const auto parts = Array::split_key(Array::subsep_key({"web", "500"}));
    check_eq(parts.size(), std::size_t{2}, "ключ розбирається назад");
    check_eq(parts[0], std::string("web"), "перша складова");
    check_eq(parts[1], std::string("500"), "друга складова");

    // Порядок обходу.
    Array counts;
    counts.lookup("10").assign_number(55);
    counts.lookup("9").assign_number(10);
    counts.lookup("100").assign_number(30);

    const auto by_index_str = counts.keys(Order::IndexStrAsc);
    check_eq(by_index_str[0], std::string("10"), "@ind_str_asc: \"10\" перед \"100\"");
    check_eq(by_index_str[2], std::string("9"), "@ind_str_asc: \"9\" останній");

    const auto by_index_num = counts.keys(Order::IndexNumAsc);
    check_eq(by_index_num[0], std::string("9"), "@ind_num_asc: 9 перший");
    check_eq(by_index_num[2], std::string("100"), "@ind_num_asc: 100 останній");

    const auto by_value = counts.keys(Order::ValueNumDesc);
    check_eq(by_value[0], std::string("10"), "@val_num_desc: найбільше значення першим");
    check_eq(by_value[2], std::string("9"), "@val_num_desc: найменше останнім");
}

} // namespace

int main()
{
    test_fnv1a();
    test_comparison_matrix();
    test_conversions();
    test_array();

    std::printf("перевірок %d, не пройшло %d\n", checks, failures);
    return failures == 0 ? 0 : 1;
}

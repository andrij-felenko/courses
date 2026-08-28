#include <cassert>

int main()
{
    // [7, 4]: рядки P скопійовані з матриці рівно так, як вона надрукована
    LinearCode code(7, 4, { bits("110"), bits("011"), bits("111"), bits("101") });

    // Самоперевірка 1: H·Gᵀ = 0 — кожен рядок G мусить бути кодовим словом.
    for (int j = 0; j < code.k(); ++j)
        assert(code.syndrome(code.encode(word{1} << j)) == 0);

    // Самоперевірка 2: будь-яка одинична помилка декодується сама в себе.
    // Синдром не залежить від даних, тож нульового слова досить для всіх 2ᵏ.
    word zero = code.encode(0);
    for (int i = 0; i < code.n(); ++i) {
        auto fix = code.decode(zero ^ (word{1} << i));
        assert(fix.data == 0 && fix.err == (word{1} << i));
    }

    // Робочий приклад.
    word m = bits("1011");
    word c = code.encode(m);            // 1011100: дані + три біти надлишку
    word r = c ^ (word{1} << 2);        // канал перевернув біт з індексом 2
    auto fix = code.decode(r);
    assert(fix.data == m && fix.err == (word{1} << 2));
    assert(code.syndromeByRows(r) == code.syndrome(r));   // обидва шляхи згодні
}

#include <cstdint>

/* a·b mod n без утрати старших бітів. Для n > 2³² добуток двох лишків
   не влазить у 64 біти: uint64_t мовчки викине старшу половину й
   поверне правдоподібне сміття. Тому множимо у 128 бітах і аж тоді
   беремо остачу. (unsigned __int128 — розширення GCC/Clang; під MSVC
   те саме роблять _umul128 + _udiv128.) */
static uint64_t mulmod(uint64_t a, uint64_t b, uint64_t n) {
    return (uint64_t)((unsigned __int128)a * b % n);
}

uint64_t powmod(uint64_t a, uint64_t k, uint64_t n) {
    uint64_t r = 1;                    // накопичувач: тут росте відповідь
    a %= n;
    while (k > 0) {
        if (k & 1)                     // цей степінь двійки є в розкладі k?
            r = mulmod(r, a, n);       // так → вкручуємо поточну ланку
        a = mulmod(a, a, n);           // наступна ланка: a, a², a⁴, a⁸, …
        k >>= 1;                       // наступний біт показника
    }
    return r;
}
/* powmod(13, 27, 55) == 7 */

#include <concepts>
#include <cstddef>
#include <cstdio>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

struct Tally { int made = 0, copied = 0, moved = 0; };
Tally tally;
bool verbose = true;

// printf міряє ширину в байтах, а не в літерах, тож вирівнюємо самі
std::string pad(const char* s, std::size_t width) {
    std::string out = s;
    std::size_t letters = 0;
    for (unsigned char ch : out)
        if ((ch & 0xC0) != 0x80) ++letters;      // байти-продовження не рахуємо
    while (letters < width) { out += ' '; ++letters; }
    return out;
}

void reset() { tally = Tally{}; }

void numbers() {
    std::printf("      = конструктори %d, копії %d, переміщення %d\n",
                tally.made, tally.copied, tally.moved);
}

#include <cstring>

// забрати до n байтів суцільним блоком; повертає скільки реально віддав
size_t Ring::popBlock(uint8_t *dst, size_t n) {
    if (n > count_) n = count_;            // не більше, ніж є
    size_t first = SIZE - tail_;          // до фізичного краю масиву
    if (first > n) first = n;
    std::memcpy(dst,         &buf_[tail_], first);    // частина 1: tail..край
    std::memcpy(dst + first, &buf_[0],     n - first); // частина 2: з початку
    tail_  = (tail_ + n) & MASK;
    count_ -= static_cast<uint16_t>(n);
    return n;
}

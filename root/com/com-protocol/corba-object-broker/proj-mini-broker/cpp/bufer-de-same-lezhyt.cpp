#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <array>
#include <fstream>
#include <cstdio>
#include <stdexcept>

inline bool host_is_little() {
    const uint16_t probe = 0x0001;
    uint8_t first;
    std::memcpy(&first, &probe, 1);      // memcpy, а не каст: без порушення аліасування
    return first == 1;
}

inline uint32_t bswap32(uint32_t v) {
    return (v >> 24) | ((v >> 8) & 0x0000FF00u)
         | ((v << 8) & 0x00FF0000u) | (v << 24);
}

class Out {
    std::vector<uint8_t> b_;
public:
    const std::vector<uint8_t>& bytes() const { return b_; }

    void align(size_t a) { while (b_.size() % a) b_.push_back(0); }

    void raw(const void* p, size_t n) {
        const uint8_t* s = static_cast<const uint8_t*>(p);
        b_.insert(b_.end(), s, s + n);
    }
    void u8 (uint8_t  v) { b_.push_back(v); }
    void u32(uint32_t v) { align(4); raw(&v, 4); }   // рідний порядок байтів
    void i32(int32_t  v) { align(4); raw(&v, 4); }
    void f64(double   v) { align(8); raw(&v, 8); }

    void str(const std::string& s) {
        u32(static_cast<uint32_t>(s.size() + 1));    // нуль у кінці ВХОДИТЬ у довжину
        raw(s.data(), s.size());
        b_.push_back(0);
    }
    void patch_u32(size_t at, uint32_t v) { std::memcpy(&b_[at], &v, 4); }
};

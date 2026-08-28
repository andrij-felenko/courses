class In {
    const uint8_t* p_;
    size_t n_, at_ = 0;
    bool swap_;
    void need(size_t k) const {
        if (k > n_ - at_) throw std::runtime_error("повідомлення обірване або збрехало про довжину");
    }
public:
    In(const uint8_t* p, size_t n, bool swap) : p_(p), n_(n), swap_(swap) {}

    void skip(size_t k)  { need(k); at_ += k; }
    void align(size_t a) { size_t k = (a - at_ % a) % a; need(k); at_ += k; }

    void raw(void* dst, size_t k) { need(k); std::memcpy(dst, p_ + at_, k); at_ += k; }

    uint8_t  u8()  { uint8_t v; raw(&v, 1); return v; }
    uint32_t u32() { align(4); uint32_t v; raw(&v, 4); return swap_ ? bswap32(v) : v; }
    int32_t  i32() { return static_cast<int32_t>(u32()); }

    std::string str() {
        uint32_t len = u32();
        if (len == 0) throw std::runtime_error("рядок без нуля в кінці");
        need(len);                                   // перевірка ДО виділення пам'яті
        std::string s(len - 1, '\0');
        raw(&s[0], len - 1);
        if (u8() != 0) throw std::runtime_error("рядок без нуля в кінці");
        return s;
    }
    std::vector<uint8_t> octets(uint32_t k) {
        need(k);
        std::vector<uint8_t> v(k);
        raw(v.data(), k);
        return v;
    }
};

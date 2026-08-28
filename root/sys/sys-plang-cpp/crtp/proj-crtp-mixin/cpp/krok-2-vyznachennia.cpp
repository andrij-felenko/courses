template <typename Derived>
class Checksummable {
public:
    uint32_t compute_checksum() const {
        const auto& self = *static_cast<const Derived*>(this);
        const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&self);
        uint32_t sum = 0;
        
        // Оскільки розмір sizeof(Derived) сталий, компілятор виконує векторизацію
        for (size_t i = 0; i < sizeof(Derived); ++i) {
            sum = (sum << 5) + sum + ptr[i];
        }
        return sum;
    }
};

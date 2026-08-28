class AccountSkeleton;                           // визначимо нижче

class ObjectTable {
    uint32_t incarnation_;                       // «номер життя» цього процесу
    std::vector<AccountSkeleton*> slots_;
public:
    explicit ObjectTable(uint32_t inc) : incarnation_(inc) {}

    std::array<uint8_t, 8> activate(AccountSkeleton* sk) {
        uint32_t idx = static_cast<uint32_t>(slots_.size());
        slots_.push_back(sk);
        std::array<uint8_t, 8> key{};
        std::memcpy(key.data(),     &incarnation_, 4);
        std::memcpy(key.data() + 4, &idx,          4);
        return key;                              // для клієнта — просто вісім байтів
    }

    AccountSkeleton* find(const std::vector<uint8_t>& key) const {
        if (key.size() != 8) return nullptr;
        uint32_t inc, idx;
        std::memcpy(&inc, key.data(),     4);
        std::memcpy(&idx, key.data() + 4, 4);
        if (inc != incarnation_) return nullptr; // ключ із минулого життя процесу
        return idx < slots_.size() ? slots_[idx] : nullptr;
    }
};

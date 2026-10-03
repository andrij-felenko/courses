#include <cstdint>
#include <cstddef>
#include <vector>

class BigNumLimbAdder {
public:
    static uint32_t add(std::vector<uint32_t>& res, const std::vector<uint32_t>& a, const std::vector<uint32_t>& b) {
        size_t n = a.size();
        res.resize(n);
        uint32_t carry = 0;
        for (size_t i = 0; i < n; ++i) {
            uint64_t sum = static_cast<uint64_t>(a[i]) + b[i] + carry;
            res[i] = static_cast<uint32_t>(sum);
            carry = static_cast<uint32_t>(sum >> 32);
        }
        return carry;
    }
};

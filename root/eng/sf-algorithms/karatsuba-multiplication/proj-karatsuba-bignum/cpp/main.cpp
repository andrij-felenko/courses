#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <algorithm>

class KaratsubaEngine {
public:
    static constexpr size_t Threshold = 32;

    static void multiply(std::span<const uint32_t> a,
                         std::span<const uint32_t> b,
                         std::span<uint32_t> out) {
        size_t n = a.size();
        std::vector<uint32_t> scratch(4 * n, 0);
        multiplyRecursive(a, b, out, scratch.data());
    }

private:
    static void schoolbook(std::span<const uint32_t> a,
                           std::span<const uint32_t> b,
                           std::span<uint32_t> out) {
        size_t n = a.size();
        std::fill(out.begin(), out.end(), 0);
        for (size_t i = 0; i < n; ++i) {
            if (a[i] == 0) continue;
            uint64_t carry = 0;
            for (size_t j = 0; j < n; ++j) {
                uint64_t cur = static_cast<uint64_t>(out[i + j]) +
                               static_cast<uint64_t>(a[i]) * b[j] + carry;
                out[i + j] = static_cast<uint32_t>(cur);
                carry = cur >> 32;
            }
            out[i + n] += static_cast<uint32_t>(carry);
        }
    }

    static uint32_t addN(std::span<const uint32_t> a,
                         std::span<const uint32_t> b,
                         std::span<uint32_t> out) {
        uint64_t carry = 0;
        for (size_t i = 0; i < a.size(); ++i) {
            uint64_t sum = static_cast<uint64_t>(a[i]) + b[i] + carry;
            out[i] = static_cast<uint32_t>(sum);
            carry = sum >> 32;
        }
        return static_cast<uint32_t>(carry);
    }

    static void subN(std::span<uint32_t> dst, std::span<const uint32_t> src) {
        int64_t borrow = 0;
        for (size_t i = 0; i < dst.size(); ++i) {
            int64_t diff = static_cast<int64_t>(dst[i]) - src[i] - borrow;
            if (diff < 0) {
                dst[i] = static_cast<uint32_t>(diff + 0x100000000ULL);
                borrow = 1;
            } else {
                dst[i] = static_cast<uint32_t>(diff);
                borrow = 0;
            }
        }
    }

    static void addWithOffset(std::span<uint32_t> dst,
                              std::span<const uint32_t> src,
                              size_t offset) {
        uint64_t carry = 0;
        for (size_t i = 0; i < src.size() && (offset + i) < dst.size(); ++i) {
            uint64_t sum = static_cast<uint64_t>(dst[offset + i]) + src[i] + carry;
            dst[offset + i] = static_cast<uint32_t>(sum);
            carry = sum >> 32;
        }
        for (size_t i = offset + src.size(); carry != 0 && i < dst.size(); ++i) {
            uint64_t sum = static_cast<uint64_t>(dst[i]) + carry;
            dst[i] = static_cast<uint32_t>(sum);
            carry = sum >> 32;
        }
    }

    static void multiplyRecursive(std::span<const uint32_t> a,
                                  std::span<const uint32_t> b,
                                  std::span<uint32_t> out,
                                  uint32_t* scratch) {
        size_t n = a.size();
        if (n <= Threshold) {
            schoolbook(a, b, out);
            return;
        }

        size_t m = n / 2;
        auto a_l = a.subspan(0, m);
        auto a_h = a.subspan(m, m);
        auto b_l = b.subspan(0, m);
        auto b_h = b.subspan(m, m);

        auto z0 = out.subspan(0, 2 * m);
        auto z2 = out.subspan(2 * m, 2 * m);

        uint32_t* z_mid_ptr = scratch;
        uint32_t* sum_a_ptr = scratch + 2 * m;
        uint32_t* sum_b_ptr = scratch + 3 * m;
        uint32_t* sub_scratch = scratch + 4 * m;

        std::span<uint32_t> z_mid(z_mid_ptr, 2 * m);
        std::span<uint32_t> sum_a(sum_a_ptr, m);
        std::span<uint32_t> sum_b(sum_b_ptr, m);

        // 1. Z0 = a_l * b_l
        multiplyRecursive(a_l, b_l, z0, sub_scratch);

        // 2. Z2 = a_h * b_h
        multiplyRecursive(a_h, b_h, z2, sub_scratch);

        // 3. Суми половин
        uint32_t carry_a = addN(a_l, a_h, sum_a);
        uint32_t carry_b = addN(b_l, b_h, sum_b);

        // 4. Z_mid = (a_l + a_h) * (b_l + b_h)
        multiplyRecursive(sum_a, sum_b, z_mid, sub_scratch);

        // Корекція перенесень
        if (carry_a != 0) addWithOffset(z_mid, sum_b, m);
        if (carry_b != 0) addWithOffset(z_mid, sum_a, m);

        // 5. Z1 = Z_mid - Z0 - Z2
        subN(z_mid, z0);
        subN(z_mid, z2);

        // 6. Додавання Z1 зі зсувом
        addWithOffset(out, z_mid, m);
    }
};

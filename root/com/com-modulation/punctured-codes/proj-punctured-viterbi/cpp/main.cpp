#include <iostream>
#include <vector>
#include <span>
#include <array>

class RateAdapter {
public:
    // Період p = 3, швидкість R = 3/4 для материнського коду R0 = 1/2
    static constexpr std::array<std::array<bool, 3>, 2> PUNC_MASK_3_4 = {{
        {true, true, false},
        {true, false, true}
    }};

    // Кодувальник виколювання R = 3/4
    [[nodiscard]] static std::vector<int> puncture(std::span<const int> mother_bits) {
        const size_t n_pairs = mother_bits.size() / 2;
        std::vector<int> result;
        result.reserve((n_pairs * 4) / 3);

        for (size_t i = 0; i < n_pairs; ++i) {
            const size_t phase = i % 3;
            const int v1 = mother_bits[2 * i + 0];
            const int v2 = mother_bits[2 * i + 1];

            if (PUNC_MASK_3_4[0][phase]) {
                result.push_back(v1);
            }
            if (PUNC_MASK_3_4[1][phase]) {
                result.push_back(v2);
            }
        }
        return result;
    }

    // Девіколювач на приймачі (вставляння LLR = 0.0f)
    [[nodiscard]] static std::vector<float> depuncture(std::span<const float> channel_llr, size_t n_pairs) {
        std::vector<float> restored_llr(n_pairs * 2, 0.0f);
        size_t rx_idx = 0;

        for (size_t i = 0; i < n_pairs; ++i) {
            const size_t phase = i % 3;

            if (PUNC_MASK_3_4[0][phase]) {
                restored_llr[2 * i + 0] = channel_llr[rx_idx++];
            } // інакше залишається 0.0f (стирання)

            if (PUNC_MASK_3_4[1][phase]) {
                restored_llr[2 * i + 1] = channel_llr[rx_idx++];
            } // інакше залишається 0.0f (стирання)
        }
        return restored_llr;
    }
};

int main() {
    const std::vector<int> mother_stream = {1, 1,  1, 0,  0, 1};
    const auto punctured = RateAdapter::puncture(mother_stream);

    std::cout << "Виколотий потік (C++): ";
    for (int b : punctured) {
        std::cout << b << " ";
    }
    std::cout << "\n";

    const std::vector<float> channel_llr = {2.5f, 1.8f, 2.1f, -1.9f};
    const auto restored = RateAdapter::depuncture(channel_llr, 3);

    std::cout << "Відновлений LLR потік для декодера:\n";
    for (size_t i = 0; i < restored.size() / 2; ++i) {
        std::cout << "Такт " << (i + 1) << ": v1 = " << restored[2 * i]
                  << ", v2 = " << restored[2 * i + 1] << "\n";
    }

    return 0;
}

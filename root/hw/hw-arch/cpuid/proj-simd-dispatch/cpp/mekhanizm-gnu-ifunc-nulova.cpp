#include <iostream>
#include <array>
#include <span>

extern "C" {
    static VecSumFn resolve_vec_sum_cpp() noexcept {
        const auto caps = CpuFeatureDetector::probe();
        if (caps.has_avx2 && caps.has_fma) {
            return VectorKernels::sum_avx2;
        }
        return VectorKernels::sum_scalar;
    }

    float fast_vec_sum(std::span<const float> data) noexcept
        __attribute__((ifunc("resolve_vec_sum_cpp")));
}

int main() {
    constexpr std::array<float, 16> numbers{
        1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f, 7.0f, 8.0f,
        9.0f, 10.0f, 11.0f, 12.0f, 13.0f, 14.0f, 15.0f, 16.0f
    };

    const float result = fast_vec_sum(numbers);
    std::cout << "Обчислена сума: " << result << "\n";
    return (result > 0.0f) ? 0 : 1;
}

// bench_wc.cpp — Ідіоматичний C++20 бенчмарк пропускної здатності пам'яті
#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <memory>
#include <cstdlib>
#include <immintrin.h>

namespace {

constexpr size_t buffer_size_bytes = 64 * 1024 * 1024; // 64 МіБ
constexpr int iterations = 20;

// Спеціальний засіб виділення вирівняної пам'яті за RAII
struct aligned_deleter {
    void operator()(void* ptr) const noexcept {
        std::free(ptr);
    }
};

using aligned_buffer = std::unique_ptr<std::byte[], aligned_deleter>;

aligned_buffer make_aligned_buffer(size_t bytes, size_t alignment = 64) {
    void* raw = nullptr;
    if (posix_memalign(&raw, alignment, bytes) != 0) {
        throw std::bad_alloc();
    }
    return aligned_buffer(static_cast<std::byte*>(raw));
}

// 1. Скалярний запис (Write-Back)
void write_scalar(std::span<uint64_t> buf, uint64_t val) noexcept {
    for (auto& item : buf) {
        item = val;
    }
}

// 2. Векторний кешований запис (AVX2 Write-Back)
void write_avx2_cached(std::span<std::byte> buf, __m256i val) noexcept {
    auto* ptr = reinterpret_cast<__m256i*>(buf.data());
    const size_t count = buf.size() / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_storeu_si256(&ptr[i], val);
    }
}

// 3. Потоковий нетемпоральний запис (Write-Combining через LFB)
void write_avx2_stream(std::span<std::byte> buf, __m256i val) noexcept {
    auto* ptr = reinterpret_cast<__m256i*>(buf.data());
    const size_t count = buf.size() / sizeof(__m256i);
    for (size_t i = 0; i < count; ++i) {
        _mm256_stream_si256(&ptr[i], val);
    }
    _mm_sfence();
}

template <typename Func>
double measure_throughput_gb_per_sec(Func&& fn) {
    const auto t0 = std::chrono::high_resolution_clock::now();
    for (int it = 0; it < iterations; ++it) {
        fn(it);
    }
    const auto t1 = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double> diff = t1 - t0;
    const double total_gb = (static_cast<double>(buffer_size_bytes) * iterations) /
                            (1024.0 * 1024.0 * 1024.0);
    return total_gb / diff.count();
}

} // namespace

int main() {
    try {
        auto mem = make_aligned_buffer(buffer_size_bytes, 64);
        std::span<std::byte> byte_view(mem.get(), buffer_size_bytes);
        std::span<uint64_t> u64_view(reinterpret_cast<uint64_t*>(mem.get()),
                                     buffer_size_bytes / sizeof(uint64_t));

        const __m256i pattern = _mm256_set1_epi64x(0xAAAAAAAAAAAAAAAAULL);

        std::cout << "=== C++20 Бенчмарк пропускної здатності запису (64 МіБ) ===\n";

        const double scalar_speed = measure_throughput_gb_per_sec([&](int it) {
            write_scalar(u64_view, 0xAAAAAAAAAAAAAAAAULL + it);
        });
        std::cout << "[1] Скалярний Write-Back (RFO):       " << scalar_speed << " ГБ/с\n";

        const double avx_speed = measure_throughput_gb_per_sec([&](int) {
            write_avx2_cached(byte_view, pattern);
        });
        std::cout << "[2] Векторний AVX2 Write-Back:         " << avx_speed << " ГБ/с\n";

        const double stream_speed = measure_throughput_gb_per_sec([&](int) {
            write_avx2_stream(byte_view, pattern);
        });
        std::cout << "[3] Потоковий Write-Combining (NT):   " << stream_speed << " ГБ/с\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}

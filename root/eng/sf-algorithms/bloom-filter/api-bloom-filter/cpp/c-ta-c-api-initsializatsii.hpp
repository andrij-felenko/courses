#include <memory>
#include <cstddef>

namespace sys {

class bloom_filter_factory {
public:
    // Фабричний метод створення фільтра з логуванням та обробкою винятків
    [[nodiscard]] static std::unique_ptr<bloom_filter> create(
        std::size_t capacity, 
        double target_fp_rate
    );

    // Створення фільтра з явним вказуванням розмірів вектору m і k
    [[nodiscard]] static std::unique_ptr<bloom_filter> create_explicit(
        std::size_t num_bits, 
        std::size_t num_hashes
    );
};

} // namespace sys

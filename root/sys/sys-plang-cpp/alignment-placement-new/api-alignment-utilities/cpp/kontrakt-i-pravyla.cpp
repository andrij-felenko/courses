#include <memory>
#include <numeric>
#include <span>

void process_floats_avx(float* raw_data, std::size_t count) {
    // Повідомляємо компілятору, що raw_data гарантовано вирівняний по межі 64 байтів
    float* aligned_data = std::assume_aligned<64>(raw_data);
    
    // Компілятор може безпечно розгорнути цикл у векторні інструкції vmovaps
    for (std::size_t i = 0; i < count; ++i) {
        aligned_data[i] *= 2.0f;
    }
}

void compute_heavy_batch(std::span<const float> data, std::stop_token stoken) {
    constexpr std::size_t CheckInterval = 1024;
    
    for (std::size_t i = 0; i < data.size(); i += CheckInterval) {
        // Перевіряємо статус скасування лише один раз на кожні 1024 елементи
        if (stoken.stop_requested()) {
            break;
        }

        const std::size_t current_chunk = std::min(CheckInterval, data.size() - i);
        process_simd_chunk(&data[i], current_chunk);
    }
}

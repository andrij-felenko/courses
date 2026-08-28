#include <iostream>
#include <cstdint>
#include <memory>

int main() {
    ShaperConfig cfg;
    cfg.cir_bytes_per_sec = 100000; // 100 КБ/с
    cfg.cbs_bytes = 10000;          // 10 КБ
    cfg.max_queue_bytes = 50000;
    cfg.mode = ShaperMode::Shape;

    TokenBucketShaper shaper(cfg);

    std::uint64_t time_us = 0;
    std::cout << "Старт: Жетонів = " << shaper.get_tokens() << " B\n";

    auto r1 = shaper.process_packet(8000, time_us);
    std::cout << "Пакет 1 (8000 B): код = " << static_cast<int>(r1)
              << ", залишок = " << shaper.get_tokens() << " B\n";

    auto r2 = shaper.process_packet(5000, time_us);
    std::cout << "Пакет 2 (5000 B): код = " << static_cast<int>(r2)
              << ", залишок = " << shaper.get_tokens() << " B\n";

    time_us += 50000; // +50 мс
    auto r3 = shaper.process_packet(5000, time_us);
    std::cout << "Пакет 3 через 50 мс (5000 B): код = " << static_cast<int>(r3)
              << ", залишок = " << shaper.get_tokens() << " B\n";

    return 0;
}

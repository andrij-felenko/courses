#include <cstdint>
#include <iostream>
#include <span>
#include <algorithm>

namespace memory {

[[nodiscard]] bool check_segment_collisions(std::span<const elf::ProgramHeader32> segments) noexcept {
    for (std::size_t i = 0; i < segments.size(); ++i) {
        if (segments[i].type != elf::SegmentType::Load || segments[i].file_size == 0) continue;

        const auto start_i = segments[i].paddr;
        const auto end_i   = start_i + segments[i].file_size;

        for (std::size_t j = i + 1; j < segments.size(); ++j) {
            if (segments[j].type != elf::SegmentType::Load || segments[j].file_size == 0) continue;

            const auto start_j = segments[j].paddr;
            const auto end_j   = start_j + segments[j].file_size;

            const auto max_start = std::max(start_i, start_j);
            const auto min_end   = std::min(end_i, end_j);

            if (max_start < min_end) {
                std::cerr << "КРИТИЧНА ПОМИЛКА: Знайдено накладання пам'яті між сегментами #" 
                          << i << " та #" << j << "!\n";
                return false;
            }
        }
    }
    return true;
}

} // namespace memory

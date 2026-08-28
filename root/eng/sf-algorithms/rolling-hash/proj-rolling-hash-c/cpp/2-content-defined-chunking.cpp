#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>

struct Chunk {
    size_t start_offset;
    size_t length;
    uint64_t boundary_hash;
};

class ContentDefinedChunker {
private:
    static constexpr uint64_t B = 257;
    static constexpr uint64_t P = 1000000007;

public:
    static std::vector<Chunk> chunk_data(const std::vector<uint8_t>& data,
                                          size_t window_size = 16,
                                          size_t target_chunk_size = 64) {
        std::vector<Chunk> chunks;
        size_t n = data.size();
        if (n == 0) return chunks;

        uint64_t mask = target_chunk_size - 1; // Для швидкості (target_chunk_size є ступенем 2)

        // E = B^(window_size - 1) % P
        uint64_t E = 1;
        for (size_t i = 0; i < window_size - 1; ++i) {
            E = (E * B) % P;
        }

        uint64_t current_hash = 0;
        size_t chunk_start = 0;

        for (size_t i = 0; i < n; ++i) {
            // Оновлюємо хеш поточного вікна
            if (i < window_size) {
                current_hash = (current_hash * B + data[i]) % P;
            } else {
                uint64_t leading = data[i - window_size];
                uint64_t trailing = data[i];

                uint64_t term = (leading * E) % P;
                uint64_t sub = (current_hash >= term) ? (current_hash - term) : (current_hash + P - term);
                current_hash = (sub * B + trailing) % P;
            }

            // Перевіряємо умову межі блоку (або досягнення максимального розміру)
            size_t current_chunk_len = i - chunk_start + 1;
            bool is_boundary = (i >= window_size - 1) && ((current_hash & mask) == 0);
            bool is_max_size = (current_chunk_len >= target_chunk_size * 4);

            if (is_boundary || is_max_size || i == n - 1) {
                chunks.push_back({chunk_start, current_chunk_len, current_hash});
                chunk_start = i + 1;
            }
        }

        return chunks;
    }
};

int main() {
    // Ґенеруємо тестовий масив байтів із повторюваними 패턴ами
    std::vector<uint8_t> stream(512);
    for (size_t i = 0; i < stream.size(); ++i) {
        stream[i] = static_cast<uint8_t>((i * 13 + 7) % 256);
    }

    auto chunks = ContentDefinedChunker::chunk_data(stream, 16, 64);

    std::cout << "Згенеровано " << chunks.size() << " динамічних блоків (CDC):\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "№   | Зсув (байтів) | Довжина (байтів) | Хеш межі\n";
    std::cout << "--------------------------------------------------------\n";
    for (size_t i = 0; i < chunks.size(); ++i) {
        std::cout << std::setw(3) << i + 1 << " | "
                  << std::setw(13) << chunks[i].start_offset << " | "
                  << std::setw(16) << chunks[i].length << " | 0x"
                  << std::hex << chunks[i].boundary_hash << std::dec << "\n";
    }

    return 0;
}

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <charconv>
#include <numeric>
#include <iomanip>

namespace benchmark {

// 1. Schema-on-write структура
struct SensorRecord {
    uint32_t id;
    float temperature;
    uint32_t timestamp;
    char status[8];
};

// 2. Schema-on-read контейнер
struct RawRecord {
    std::string raw;
};

// Швидкий парсер рядків через std::string_view та std::from_chars
bool extract_temp_fast(std::string_view raw, float& out_temp) {
    constexpr std::string_view key = "temp=";
    auto pos = raw.find(key);
    if (pos == std::string_view::npos) return false;

    raw.remove_prefix(pos + key.size());
    auto end_pos = raw.find(';');
    if (end_pos != std::string_view::npos) {
        raw = raw.substr(0, end_pos);
    }

    auto res = std::from_chars(raw.data(), raw.data() + raw.size(), out_temp);
    return res.ec == std::errc{};
}

} // namespace benchmark

int main() {
    using namespace benchmark;
    constexpr int kRecords = 100000;

    std::vector<SensorRecord> write_db;
    std::vector<RawRecord> read_db;
    write_db.reserve(kRecords);
    read_db.reserve(kRecords);

    for (int i = 0; i < kRecords; ++i) {
        float temp = 20.0f + static_cast<float>(i % 100) * 0.1f;
        write_db.push_back({static_cast<uint32_t>(i), temp, static_cast<uint32_t>(1700000000 + i), "ACTIVE"});
        
        std::string raw = "id=" + std::to_string(i) + ";temp=" + std::to_string(temp) + ";ts=" + std::to_string(1700000000 + i);
        read_db.push_back({std::move(raw)});
    }

    // 1. Schema-on-write Агрегація
    auto t0 = std::chrono::high_resolution_clock::now();
    double sum_write = 0.0;
    for (const auto& rec : write_db) {
        sum_write += rec.temperature;
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    double dur_write = std::chrono::duration<double, std::milli>(t1 - t0).count();

    // 2. Schema-on-read Агрегація
    auto t2 = std::chrono::high_resolution_clock::now();
    double sum_read = 0.0;
    for (const auto& rec : read_db) {
        float temp = 0.0f;
        if (extract_temp_fast(rec.raw, temp)) {
            sum_read += temp;
        }
    }
    auto t3 = std::chrono::high_resolution_clock::now();
    double dur_read = std::chrono::duration<double, std::milli>(t3 - t2).count();

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Результати C++ бенчмарку (" << kRecords << " записів) ===\n";
    std::cout << "Schema-on-write: " << dur_write << " мс\n";
    std::cout << "Schema-on-read:  " << dur_read << " мс\n";
    std::cout << "Співвідношення швидкості: " << (dur_read / dur_write) << "x на користь Schema-on-write\n";

    return 0;
}

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <fstream>
#include <filesystem>
#include <memory>
#include <chrono>
#include <expected>
#include <cstdint>
#include <cstring>

namespace fs = std::filesystem;

namespace eventlog {

constexpr size_t INDEX_INTERVAL_BYTES = 4096;

#pragma pack(push, 1)
struct IndexEntry {
    uint32_t relative_offset{0};
    uint32_t physical_pos{0};
};
#pragma pack(pop)

/* Клас сегмента журналу з безпечним RAII-керуванням ресурсами */
class LogSegment {
public:
    static std::expected<std::unique_ptr<LogSegment>, std::string>
    open(const fs::path& dir, uint64_t base_offset) {
        char name_buf[64];
        std::snprintf(name_buf, sizeof(name_buf), "%020llu", static_cast<unsigned long long>(base_offset));

        auto log_p = dir / (std::string(name_buf) + ".log");
        auto idx_p = dir / (std::string(name_buf) + ".index");

        auto seg = std::unique_ptr<LogSegment>(new LogSegment(base_offset, log_p, idx_p));
        if (!seg->init()) {
            return std::unexpected("Не вдалося відкрити файли сегмента: " + log_p.string());
        }
        return seg;
    }

    ~LogSegment() {
        flush();
    }

    LogSegment(const LogSegment&) = delete;
    LogSegment& operator=(const LogSegment&) = delete;

    LogSegment(LogSegment&&) noexcept = default;
    LogSegment& operator=(LogSegment&&) noexcept = default;

    /* Додавання нового повідомлення у кінець сегмента */
    std::expected<uint64_t, std::string>
    append(std::string_view key, std::string_view value) {
        if (!log_stream_.is_open() || !idx_stream_.is_open()) {
            return std::unexpected("Файли сегмента не готові до запису");
        }

        uint64_t offset = next_offset_;
        uint64_t now_ms = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count()
        );

        uint32_t record_pos = current_log_size_;
        int32_t key_len = static_cast<int32_t>(key.size());
        int32_t val_len = static_cast<int32_t>(value.size());

        // Формування бінарного тіла фрейму
        std::vector<uint8_t> payload;
        payload.reserve(1 + 1 + 8 + 8 + 4 + key.size() + 4 + value.size());

        uint8_t magic = 0x01;
        uint8_t flags = 0x00;
        append_bytes(payload, &magic, 1);
        append_bytes(payload, &flags, 1);
        append_bytes(payload, &offset, sizeof(offset));
        append_bytes(payload, &now_ms, sizeof(now_ms));
        append_bytes(payload, &key_len, sizeof(key_len));
        if (!key.empty()) append_bytes(payload, key.data(), key.size());
        append_bytes(payload, &val_len, sizeof(val_len));
        if (!value.empty()) append_bytes(payload, value.data(), value.size());

        uint32_t crc = calculate_crc32(payload.data(), payload.size());

        // Фізичний запис у файл .log
        log_stream_.write(reinterpret_cast<const char*>(&crc), sizeof(crc));
        log_stream_.write(reinterpret_cast<const char*>(payload.data()), payload.size());

        if (log_stream_.bad()) {
            return std::unexpected("Помилка вводу-виводу при записі в .log");
        }

        size_t total_bytes = sizeof(crc) + payload.size();
        current_log_size_ += static_cast<uint32_t>(total_bytes);
        bytes_since_last_index_ += static_cast<uint32_t>(total_bytes);

        // Додавання мітки до розрідженого індексу
        if (bytes_since_last_index_ >= INDEX_INTERVAL_BYTES || offset == base_offset_) {
            IndexEntry entry{
                .relative_offset = static_cast<uint32_t>(offset - base_offset_),
                .physical_pos = record_pos
            };
            idx_stream_.write(reinterpret_cast<const char*>(&entry), sizeof(entry));
            idx_stream_.flush();
            bytes_since_last_index_ = 0;
        }

        log_stream_.flush();
        next_offset_++;
        return offset;
    }

    /* Швидкий пошук за зсувом через індекс */
    std::expected<std::string, std::string>
    read_at(uint64_t target_offset) {
        if (target_offset < base_offset_ || target_offset >= next_offset_) {
            return std::unexpected("Запитуваний зсув знаходиться поза межами цього сегмента");
        }

        // 1. Двійковий пошук найближчого меншого зсуву в .index
        std::ifstream idx_in(idx_path_, std::ios::binary | std::ios::ate);
        if (!idx_in.is_open()) return std::unexpected("Не вдалося відкрити індексний файл");

        auto idx_size = idx_in.tellg();
        size_t num_entries = idx_size / sizeof(IndexEntry);

        uint32_t search_rel = static_cast<uint32_t>(target_offset - base_offset_);
        uint32_t best_pos = 0;

        int low = 0, high = static_cast<int>(num_entries) - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;
            idx_in.seekg(mid * sizeof(IndexEntry));
            IndexEntry entry;
            idx_in.read(reinterpret_cast<char*>(&entry), sizeof(entry));

            if (entry.relative_offset <= search_rel) {
                best_pos = entry.physical_pos;
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        idx_in.close();

        // 2. Послідовне сканування логу від знайденої точки (максимум 4 КБ)
        std::ifstream log_in(log_path_, std::ios::binary);
        if (!log_in.is_open()) return std::unexpected("Не вдалося відкрити лог для читання");

        log_in.seekg(best_pos);

        while (log_in.tellg() < current_log_size_ && log_in.good()) {
            uint32_t crc;
            uint8_t magic, flags;
            uint64_t rec_offset, ts;
            int32_t klen, vlen;

            log_in.read(reinterpret_cast<char*>(&crc), sizeof(crc));
            log_in.read(reinterpret_cast<char*>(&magic), sizeof(magic));
            log_in.read(reinterpret_cast<char*>(&flags), sizeof(flags));
            log_in.read(reinterpret_cast<char*>(&rec_offset), sizeof(rec_offset));
            log_in.read(reinterpret_cast<char*>(&ts), sizeof(ts));
            log_in.read(reinterpret_cast<char*>(&klen), sizeof(klen));

            if (klen > 0) log_in.seekg(klen, std::ios::cur);
            log_in.read(reinterpret_cast<char*>(&vlen), sizeof(vlen));

            if (rec_offset == target_offset) {
                std::string result(vlen, '\0');
                if (vlen > 0) log_in.read(result.data(), vlen);
                return result;
            }

            if (vlen > 0) log_in.seekg(vlen, std::ios::cur);
        }

        return std::unexpected("Запис не знайдено в журналі");
    }

    [[nodiscard]] uint64_t base_offset() const noexcept { return base_offset_; }
    [[nodiscard]] uint64_t next_offset() const noexcept { return next_offset_; }
    [[nodiscard]] uint32_t size_bytes() const noexcept { return current_log_size_; }

private:
    LogSegment(uint64_t base_offset, fs::path log_p, fs::path idx_p)
        : base_offset_(base_offset), next_offset_(base_offset),
          log_path_(std::move(log_p)), idx_path_(std::move(idx_p)) {}

    bool init() {
        log_stream_.open(log_path_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);
        idx_stream_.open(idx_path_, std::ios::in | std::ios::out | std::ios::binary | std::ios::app);

        if (!log_stream_.is_open() || !idx_stream_.is_open()) return false;

        log_stream_.seekp(0, std::ios::end);
        current_log_size_ = static_cast<uint32_t>(log_stream_.tellp());
        return true;
    }

    void flush() {
        if (log_stream_.is_open()) log_stream_.flush();
        if (idx_stream_.is_open()) idx_stream_.flush();
    }

    static void append_bytes(std::vector<uint8_t>& buf, const void* data, size_t sz) {
        const auto* ptr = static_cast<const uint8_t*>(data);
        buf.insert(buf.end(), ptr, ptr + sz);
    }

    static uint32_t calculate_crc32(const uint8_t* data, size_t length) {
        uint32_t crc = 0;
        for (size_t i = 0; i < length; ++i) {
            uint8_t byte = data[i];
            crc ^= byte;
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return crc;
    }

    uint64_t base_offset_{0};
    uint64_t next_offset_{0};
    uint32_t current_log_size_{0};
    uint32_t bytes_since_last_index_{0};

    fs::path log_path_;
    fs::path idx_path_;
    std::fstream log_stream_;
    std::fstream idx_stream_;
};

} // namespace eventlog

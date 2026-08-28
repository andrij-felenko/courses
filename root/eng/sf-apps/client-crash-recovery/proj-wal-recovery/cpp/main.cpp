#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <chrono>
#include <numeric>
#include <stdexcept>
#include <span>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <sys/file.h>
#endif

namespace fs = std::filesystem;

// ── Алгоритм CRC32 (IEEE 802.3) ─────────────────────────────────────────────
class Crc32 {
public:
    static uint32_t calculate(std::span<const uint8_t> data) {
        uint32_t crc = 0xFFFFFFFFu;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int k = 0; k < 8; ++k) {
                crc = (crc >> 1) ^ (0xEDB88320u & -(crc & 1));
            }
        }
        return ~crc;
    }
};

// ── Заголовок запису в журналі WAL ──────────────────────────────────────────
#pragma pack(push, 1)
struct WalHeader {
    uint32_t magic;       // 0x57414C31 ("WAL1")
    uint64_t seq_num;     // Монотонний номер операції
    int64_t  timestamp;   // Час створення в мілісекундах
    uint32_t payload_len; // Довжина тіла операції в байтах
};
#pragma pack(pop)

constexpr uint32_t WAL_MAGIC = 0x57414C31;

// ── Документ у пам'яті (проста модель текстових рядків) ─────────────────────
class DocumentModel {
public:
    void apply_operation(std::string_view op) {
        // Формат операції: "INSERT:<рядок>" або "CLEAR"
        if (op.starts_with("INSERT:")) {
            lines_.emplace_back(op.substr(7));
        } else if (op == "CLEAR") {
            lines_.clear();
        }
    }

    [[nodiscard]] std::string serialize() const {
        std::string out;
        for (const auto& line : lines_) {
            out += line;
            out += '\n';
        }
        return out;
    }

    void deserialize(std::string_view content) {
        lines_.clear();
        size_t start = 0;
        while (start < content.size()) {
            size_t end = content.find('\n', start);
            if (end == std::string_view::npos) end = content.size();
            if (end > start) {
                lines_.emplace_back(content.substr(start, end - start));
            }
            start = end + 1;
        }
    }

    const std::vector<std::string>& get_lines() const { return lines_; }

private:
    std::vector<std::string> lines_;
};

// ── Менеджер стійкості до крахів ────────────────────────────────────────────
class CrashResilientStore {
public:
    CrashResilientStore(fs::path base_path)
        : base_path_(std::move(base_path)),
          snap_path_(base_path_.string() + ".snap"),
          wal_path_(base_path_.string() + ".wal"),
          lock_path_(base_path_.string() + ".lock") {}

    ~CrashResilientStore() {
        release_lock();
    }

    // Захоплення ексклюзивного блокування (Lease)
    bool acquire_lock() {
#if defined(_WIN32)
        lock_handle_ = CreateFileW(lock_path_.c_str(), GENERIC_READ | GENERIC_WRITE,
                                   0, nullptr, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
        return lock_handle_ != INVALID_HANDLE_VALUE;
#else
        lock_fd_ = ::open(lock_path_.c_str(), O_RDWR | O_CREAT, 0666);
        if (lock_fd_ < 0) return false;
        return ::flock(lock_fd_, LOCK_EX | LOCK_NB) == 0;
#endif
    }

    // Завантаження та відновлення стану після краху
    void recover(DocumentModel& model) {
        // Крок 1: Читання базового знімка (якщо існує)
        if (fs::exists(snap_path_)) {
            std::ifstream snap_file(snap_path_, std::ios::binary);
            std::string content((std::istreambuf_iterator<char>(snap_file)),
                                 std::istreambuf_iterator<char>());
            model.deserialize(content);
        }

        // Крок 2: Програвання операцій із журналу WAL
        if (!fs::exists(wal_path_)) return;

        std::ifstream wal_file(wal_path_, std::ios::binary);
        std::vector<uint8_t> wal_data((std::istreambuf_iterator<char>(wal_file)),
                                       std::istreambuf_iterator<char>());

        size_t offset = 0;
        size_t valid_operations = 0;

        while (offset + sizeof(WalHeader) + sizeof(uint32_t) <= wal_data.size()) {
            WalHeader header;
            std::memcpy(&header, wal_data.data() + offset, sizeof(WalHeader));

            if (header.magic != WAL_MAGIC) break;

            size_t total_record_size = sizeof(WalHeader) + header.payload_len + sizeof(uint32_t);
            if (offset + total_record_size > wal_data.size()) {
                // Розірваний запис на хвості файлу — відкидаємо
                break;
            }

            // Перевірка контрольної суми CRC32
            uint32_t stored_crc;
            std::memcpy(&stored_crc, wal_data.data() + offset + sizeof(WalHeader) + header.payload_len, sizeof(uint32_t));

            std::span<const uint8_t> payload_span(wal_data.data() + offset + sizeof(WalHeader), header.payload_len);
            uint32_t computed_crc = Crc32::calculate(payload_span);

            if (computed_crc != stored_crc) {
                // Пошкодження даних — зупиняємо повтор на останньому валідному записі
                break;
            }

            std::string op(reinterpret_cast<const char*>(payload_span.data()), payload_span.size());
            model.apply_operation(op);

            seq_num_ = std::max(seq_num_, header.seq_num);
            offset += total_record_size;
            valid_operations++;
        }

        // Крок 3: Якщо було відновлено операції, закріплюємо їх свіжим знімком
        if (valid_operations > 0) {
            checkpoint(model);
        }
    }

    // Запис нової операції в журнал WAL
    void append_operation(std::string_view op) {
        std::vector<uint8_t> buffer;
        WalHeader header;
        header.magic = WAL_MAGIC;
        header.seq_num = ++seq_num_;
        header.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
        header.payload_len = static_cast<uint32_t>(op.size());

        auto header_bytes = reinterpret_cast<const uint8_t*>(&header);
        buffer.insert(buffer.end(), header_bytes, header_bytes + sizeof(WalHeader));

        auto op_bytes = reinterpret_cast<const uint8_t*>(op.data());
        buffer.insert(buffer.end(), op_bytes, op_bytes + op.size());

        std::span<const uint8_t> payload_span(op_bytes, op.size());
        uint32_t crc = Crc32::calculate(payload_span);
        auto crc_bytes = reinterpret_cast<const uint8_t*>(&crc);
        buffer.insert(buffer.end(), crc_bytes, crc_bytes + sizeof(uint32_t));

        // Дописування у файл
        std::ofstream wal_out(wal_path_, std::ios::binary | std::ios::app);
        wal_out.write(reinterpret_cast<const char*>(buffer.data()), buffer.size());
        wal_out.flush();
    }

    // Створення контрольної точки (Checkpoint): атомарний знімок + очищення WAL
    void checkpoint(const DocumentModel& model) {
        fs::path tmp_snap = snap_path_.string() + ".tmp";
        std::string serialized = model.serialize();

        // 1. Запис у тимчасовий файл
        {
            std::ofstream out(tmp_snap, std::ios::binary | std::ios::trunc);
            out.write(serialized.data(), serialized.size());
            out.flush();
        }

        // 2. Атомарна підміна файлу
        fs::rename(tmp_snap, snap_path_);

        // 3. Обрізання журналу WAL
        std::ofstream wal_truncate(wal_path_, std::ios::binary | std::ios::trunc);
        wal_truncate.close();
    }

private:
    void release_lock() {
#if defined(_WIN32)
        if (lock_handle_ != INVALID_HANDLE_VALUE) {
            CloseHandle(lock_handle_);
            lock_handle_ = INVALID_HANDLE_VALUE;
        }
#else
        if (lock_fd_ >= 0) {
            ::flock(lock_fd_, LOCK_UN);
            ::close(lock_fd_);
            lock_fd_ = -1;
        }
#endif
    }

    fs::path base_path_;
    fs::path snap_path_;
    fs::path wal_path_;
    fs::path lock_path_;
    uint64_t seq_num_{0};

#if defined(_WIN32)
    HANDLE lock_handle_{INVALID_HANDLE_VALUE};
#else
    int lock_fd_{-1};
#endif
};

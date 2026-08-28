#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string_view>
#include <filesystem>
#include <fstream>
#include <cstdint>
#include <stdexcept>
#include <optional>
#include <unistd.h>
#include <fcntl.h>

namespace minidb {

enum class LogType : uint32_t {
    Begin = 1,
    Update = 2,
    Commit = 3,
    Abort = 4
};

#pragma pack(push, 1)
struct WalRecord {
    uint64_t lsn{0};
    uint64_t txn_id{0};
    LogType type{LogType::Begin};
    uint32_t key{0};
    int32_t old_val{0};
    int32_t new_val{0};
};
#pragma pack(pop)

struct TableEntry {
    int32_t val{0};
    uint64_t page_lsn{0};
    uint64_t lock_owner{0}; // 0 = unlocked
};

class TransactionEngine {
public:
    explicit TransactionEngine(std::string_view wal_path)
        : wal_path_(wal_path) {
        wal_fd_ = ::open(wal_path_.c_str(), O_CREAT | O_RDWR | O_APPEND, 0644);
        if (wal_fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити журнал WAL");
        }
    }

    ~TransactionEngine() noexcept {
        if (wal_fd_ >= 0) {
            ::fsync(wal_fd_);
            ::close(wal_fd_);
        }
    }

    // Заборона копіювання через володіння дескриптором файлу
    TransactionEngine(const TransactionEngine&) = delete;
    TransactionEngine& operator=(const TransactionEngine&) = delete;

    uint64_t begin_transaction() {
        uint64_t tid = next_txn_id_++;
        append_wal(tid, LogType::Begin, 0, 0, 0, false);
        return tid;
    }

    bool update(uint64_t tid, uint32_t key, int32_t new_v) {
        auto& entry = storage_[key];

        // Суворе двофазне блокування (Strict 2PL)
        if (entry.lock_owner != 0 && entry.lock_owner != tid) {
            return false; // Конфлікт блокування з іншою транзакцією
        }
        entry.lock_owner = tid;

        int32_t old_v = entry.val;
        // Undo/Redo Invariant: WAL записується ПЕРЕД оновленням пам'яті
        uint64_t lsn = append_wal(tid, LogType::Update, key, old_v, new_v, false);

        entry.val = new_v;
        entry.page_lsn = lsn;
        return true;
    }

    void commit(uint64_t tid) {
        // Durability: примусовий скид буфера WAL на постійний диск
        append_wal(tid, LogType::Commit, 0, 0, 0, true);
        release_locks(tid);
    }

    void abort(uint64_t tid) {
        // Скасування: відкат змін за допомогою записів у журналі
        rollback_active_records(tid);
        append_wal(tid, LogType::Abort, 0, 0, 0, true);
        release_locks(tid);
    }

    int32_t read(uint32_t key) const {
        auto it = storage_.find(key);
        return (it != storage_.end()) ? it->second.val : 0;
    }

    void recover() {
        if (!std::filesystem::exists(wal_path_)) return;

        int fd = ::open(wal_path_.c_str(), O_RDONLY);
        if (fd < 0) return;

        std::unordered_set<uint64_t> active_txns;
        uint64_t max_lsn = 0;
        uint64_t max_tid = 0;
        WalRecord rec;

        // Фаза 1: Аналіз активних транзакцій на момент збою
        while (::read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
            max_lsn = std::max(max_lsn, rec.lsn);
            max_tid = std::max(max_tid, rec.txn_id);

            if (rec.type == LogType::Begin) {
                active_txns.insert(rec.txn_id);
            } else if (rec.type == LogType::Commit || rec.type == LogType::Abort) {
                active_txns.erase(rec.txn_id);
            }
        }

        // Фаза 2: Повторення історії (REDO)
        ::lseek(fd, 0, SEEK_SET);
        while (::read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
            if (rec.type == LogType::Update) {
                auto& entry = storage_[rec.key];
                entry.val = rec.new_val;
                entry.page_lsn = rec.lsn;
            }
        }

        // Фаза 3: Скасування незафіксованих змін (UNDO)
        for (uint64_t uncommitted_tid : active_txns) {
            off_t pos = ::lseek(fd, 0, SEEK_END);
            while (pos >= static_cast<off_t>(sizeof(WalRecord))) {
                pos -= sizeof(WalRecord);
                ::lseek(fd, pos, SEEK_SET);
                if (::read(fd, &rec, sizeof(rec)) == sizeof(rec)) {
                    if (rec.txn_id == uncommitted_tid && rec.type == LogType::Update) {
                        storage_[rec.key].val = rec.old_val;
                    }
                }
            }
        }

        ::close(fd);
        next_lsn_ = max_lsn + 1;
        next_txn_id_ = max_tid + 1;
    }

private:
    std::string wal_path_;
    int wal_fd_{-1};
    uint64_t next_lsn_{1};
    uint64_t next_txn_id_{1};
    std::unordered_map<uint32_t, TableEntry> storage_;

    uint64_t append_wal(uint64_t tid, LogType type, uint32_t key,
                        int32_t old_v, int32_t new_v, bool flush) {
        WalRecord rec{
            .lsn = next_lsn_++,
            .txn_id = tid,
            .type = type,
            .key = key,
            .old_val = old_v,
            .new_val = new_v
        };
        ::write(wal_fd_, &rec, sizeof(rec));
        if (flush) {
            ::fsync(wal_fd_);
        }
        return rec.lsn;
    }

    void rollback_active_records(uint64_t tid) {
        off_t cur = ::lseek(wal_fd_, 0, SEEK_END);
        off_t pos = cur;
        WalRecord rec;

        while (pos >= static_cast<off_t>(sizeof(WalRecord))) {
            pos -= sizeof(WalRecord);
            ::lseek(wal_fd_, pos, SEEK_SET);
            if (::read(wal_fd_, &rec, sizeof(rec)) == sizeof(rec)) {
                if (rec.txn_id == tid && rec.type == LogType::Update) {
                    storage_[rec.key].val = rec.old_val;
                }
            }
        }
        ::lseek(wal_fd_, cur, SEEK_SET);
    }

    void release_locks(uint64_t tid) {
        for (auto& [key, entry] : storage_) {
            if (entry.lock_owner == tid) {
                entry.lock_owner = 0;
            }
        }
    }
};

} // namespace minidb

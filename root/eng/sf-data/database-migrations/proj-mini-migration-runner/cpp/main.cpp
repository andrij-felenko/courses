#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <cstdint>
#include <iomanip>
#include <algorithm>

namespace migration {

struct Migration {
    uint32_t version;
    std::string name;
    std::string up_sql;
    std::string down_sql;
    uint32_t checksum{0};
};

uint32_t djb2_hash(const std::string& str) {
    uint32_t hash = 5381;
    for (char c : str) {
        hash = ((hash << 5) + hash) + static_cast<uint8_t>(c);
    }
    return hash;
}

class MigrationRunner {
public:
    MigrationRunner() : locked_(false) {}

    void acquire_lock() {
        if (locked_) {
            throw std::runtime_error("Паралельний процес уже виконує міграцію!");
        }
        locked_ = true;
        std::cout << "[Lock] Отримано розподілене блокування schema_lock\n";
    }

    void release_lock() {
        locked_ = false;
        std::cout << "[Lock] Розподілене блокування звільнено\n";
    }

    void migrate(const std::vector<Migration>& code_migrations) {
        acquire_lock();
        try {
            // 1. Звірка історії (Checksum Verification)
            for (const auto& applied : history_) {
                auto it = std::find_if(code_migrations.begin(), code_migrations.end(), [&](const Migration& m) {
                    return m.version == applied.version;
                });
                if (it == code_migrations.end()) {
                    throw std::runtime_error("Міграція v" + std::to_string(applied.version) + " зникла з репозиторію!");
                }
                if (djb2_hash(it->up_sql) != applied.checksum) {
                    throw std::runtime_error("Файл міграції v" + std::to_string(applied.version) + " був модифікований після релізу!");
                }
            }

            // 2. Накатування нових міграцій
            for (auto m : code_migrations) {
                auto it = std::find_if(history_.begin(), history_.end(), [&](const Migration& h) {
                    return h.version == m.version;
                });
                if (it == history_.end()) {
                    std::cout << "[EXEC] Застосування v" << m.version << " (" << m.name << ")...\n";
                    std::cout << "  SQL: " << m.up_sql << "\n";
                    m.checksum = djb2_hash(m.up_sql);
                    history_.push_back(m);
                    std::cout << "[DONE] v" << m.version << " успішно зафіксовано.\n";
                }
            }
            release_lock();
        } catch (...) {
            release_lock();
            throw;
        }
    }

    void print_history() const {
        std::cout << "\n=== Таблиця schema_migrations ===\n";
        for (const auto& m : history_) {
            std::cout << "v" << m.version << " | " << std::setw(25) << std::left << m.name 
                      << " | Hash: 0x" << std::hex << m.checksum << std::dec << "\n";
        }
    }

private:
    bool locked_;
    std::vector<Migration> history_;
};

} // namespace migration

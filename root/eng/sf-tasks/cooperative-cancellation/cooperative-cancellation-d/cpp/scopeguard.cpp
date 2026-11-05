// Приклад використання RAII та Scope Guard для транзакційного відкату в C++
#include <iostream>
#include <fstream>
#include <string>
#include <stop_token>
#include <filesystem>
#include <functional>

namespace fs = std::filesystem;

// Клас Scope Guard для гарантованого очищення ресурсів
class ScopeGuard {
private:
    std::function<void()> cleanup_;
    bool dismissed_{false};

public:
    explicit ScopeGuard(std::function<void()> cleanup) : cleanup_(std::move(cleanup)) {}
    ~ScopeGuard() {
        if (!dismissed_ && cleanup_) {
            cleanup_();
        }
    }
    void dismiss() { dismissed_ = true; }
};

bool perform_task_with_rollback(const fs::path& temp_file, const fs::path& target_file, std::stop_token stoken) {
    std::ofstream out(temp_file);
    if (!out.is_open()) return false;

    // RAII/Scope Guard гарантує видалення тимчасового файла в разі винятку або скасування
    ScopeGuard rollback_guard([&temp_file]() {
        if (fs::exists(temp_file)) {
            fs::remove(temp_file);
            std::cout << "Відкат стану: тимчасовий файл видалено." << std::endl;
        }
    });

    for (int i = 0; i < 50; ++i) {
        // Перевірка точки скасування (checkpoint)
        if (stoken.stop_requested()) {
            std::cout << "Скасування виявлено на кроці " << i << std::endl;
            return false; // ScopeGuard автоматично здійснить відкат
        }

        out << "Крок обчислень " << i << "\n";
    }

    out.close();
    fs::rename(temp_file, target_file);
    rollback_guard.dismiss(); // Фіксація транзакції: відкат не потрібен
    return true;
}

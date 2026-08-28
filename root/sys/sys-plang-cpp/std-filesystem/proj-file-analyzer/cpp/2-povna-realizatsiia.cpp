#include <iostream>
#include <filesystem>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <iomanip>
#include <system_error>
#include <sstream>

namespace fs = std::filesystem;

// Структура підсумкових результатів аудиту файлової системи
struct AnalysisResult {
    std::uintmax_t total_bytes{0};
    std::uintmax_t total_files{0};
    std::uintmax_t total_directories{0};
    std::uintmax_t total_symlinks{0};
    std::uintmax_t skipped_errors{0};

    // Розподіл зайнятої пам'яті за розширеннями файлів
    std::unordered_map<std::string, std::uintmax_t> extension_bytes;

    // Список виявлених небезпечних файлів з відкритими правами
    std::vector<fs::path> insecure_files;

    // Найбільший знайдений файл під час сканування
    fs::path largest_file_path;
    std::uintmax_t largest_file_size{0};
};

class FileSystemAnalyzer {
public:
    explicit FileSystemAnalyzer(fs::path target_path)
        : target_root_(std::move(target_path)) {}

    // Головний метод запуску повного сканування
    AnalysisResult analyze() {
        AnalysisResult result;
        std::error_code ec;

        // Крок 1: Перевірка існування та статусу базового шляху
        fs::file_status root_status = fs::status(target_root_, ec);
        if (ec || !fs::exists(root_status)) {
            std::cerr << "[Помилка] Вказаний шлях не існує або недоступний: " 
                      << target_root_ << " (" << ec.message() << ")\n";
            return result;
        }

        // Крок 2: Отримання загальної інформації про дисковий простір
        fs::space_info disk_info = fs::space(target_root_, ec);
        if (!ec) {
            std::cout << "--- Інформація про дисковий розділ ---\n"
                      << " Загальна ємність: " << format_size(disk_info.capacity) << "\n"
                      << " Вільний простір:  " << format_size(disk_info.free) << "\n"
                      << " Доступно користувачу: " << format_size(disk_info.available) << "\n"
                      << "----------------------------------------\n";
        }

        // Якщо переданий шлях вказує на одиночний файл
        if (fs::is_regular_file(root_status)) {
            process_file(target_root_, result);
            return result;
        }

        // Крок 3: Налаштування рекурсивного обходу із захистом від відмови доступу
        auto options = fs::directory_options::skip_permission_denied;
        
        fs::recursive_directory_iterator it(target_root_, options, ec);
        fs::recursive_directory_iterator end_it;

        if (ec) {
            std::cerr << "[Помилка] Неможливо відкрити початковий каталог: " << ec.message() << "\n";
            return result;
        }

        while (it != end_it) {
            const fs::directory_entry& entry = *it;

            // Безпечно отримуємо статус символьного посилання із внутрішнього кешу
            fs::file_status status = entry.symlink_status(ec);
            if (ec) {
                result.skipped_errors++;
                it.increment(ec);
                continue;
            }

            // Обробка символьних посилань
            if (fs::is_symlink(status)) {
                result.total_symlinks++;
                // Перевірка на висяче посилання (dangling symlink)
                fs::file_status target_st = entry.status(ec);
                if (ec || !fs::exists(target_st)) {
                    std::cout << "[Увага] Виявлено висяче символьне посилання: " 
                              << entry.path() << "\n";
                }
            }
            // Обробка звичайних файлів
            else if (fs::is_regular_file(status)) {
                result.total_files++;
                std::uintmax_t sz = entry.file_size(ec);
                if (!ec) {
                    result.total_bytes += sz;
                    
                    // Групування обсягу за розширенням файлу
                    std::string ext = entry.path().extension().string();
                    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
                    if (ext.empty()) ext = "[без розширення]";
                    result.extension_bytes[ext] += sz;

                    // Фіксація найменшого та найбільшого файлу
                    if (sz > result.largest_file_size) {
                        result.largest_file_size = sz;
                        result.largest_file_path = entry.path();
                    }
                }

                // Перевірка безпеки прав доступу: чи відкритий файл на запис для сторонніх
                if ((status.permissions() & fs::perms::others_write) != fs::perms::none) {
                    result.insecure_files.push_back(entry.path());
                }
            }
            // Обробка каталогів
            else if (fs::is_directory(status)) {
                result.total_directories++;
            }

            // Безпечний перехід до наступного елемента без викидання винятків
            it.increment(ec);
            if (ec) {
                result.skipped_errors++;
                ec.clear();
            }
        }

        return result;
    }

    // Допоміжний метод форматування байтів у людський вигляд
    static std::string format_size(std::uintmax_t bytes) {
        constexpr double KB = 1024.0;
        constexpr double MB = KB * 1024.0;
        constexpr double GB = MB * 1024.0;

        std::ostringstream ss;
        ss << std::fixed << std::setprecision(2);
        if (bytes >= GB) ss << (bytes / GB) << " GB";
        else if (bytes >= MB) ss << (bytes / MB) << " MB";
        else if (bytes >= KB) ss << (bytes / KB) << " KB";
        else ss << bytes << " B";
        return ss.str();
    }

private:
    void process_file(const fs::path& p, AnalysisResult& res) {
        std::error_code ec;
        auto sz = fs::file_size(p, ec);
        if (!ec) {
            res.total_files = 1;
            res.total_bytes = sz;
            res.extension_bytes[p.extension().string()] = sz;
            res.largest_file_path = p;
            res.largest_file_size = sz;
        }
    }

    fs::path target_root_;
};

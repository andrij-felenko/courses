#define _GNU_SOURCE
#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <chrono>
#include <iomanip>
#include <ctime>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace fs_inspect {

/* Клас-обгортка над struct statx для ідіоматичного C++ доступу */
class StatxInfo {
public:
    static StatxInfo fetch(const std::string& path, unsigned int extra_mask = 0) {
        StatxInfo info{};
        unsigned int request_mask = STATX_BASIC_STATS | STATX_BTIME | extra_mask;
        
        int res = ::statx(AT_FDCWD, path.c_str(), AT_SYMLINK_NOFOLLOW | AT_STATX_SYNC_AS_STAT,
                          request_mask, &info.stx_);
        if (res != 0) {
            throw std::system_error(errno, std::generic_category(), 
                                    "Не вдалося виконати statx для: " + path);
        }
        return info;
    }

    [[nodiscard]] uint64_t size() const noexcept { return stx_.stx_size; }
    [[nodiscard]] uint64_t inode() const noexcept { return stx_.stx_ino; }
    [[nodiscard]] uint32_t nlink() const noexcept { return stx_.stx_nlink; }
    [[nodiscard]] uint16_t permissions() const noexcept { return stx_.stx_mode & 07777; }
#ifdef STATX_DIOALIGN
    [[nodiscard]] uint32_t dio_mem_align() const noexcept { return stx_.stx_dio_mem_align; }
#endif

    [[nodiscard]] bool has_field(uint32_t flag) const noexcept {
        return (stx_.stx_mask & flag) != 0;
    }

    [[nodiscard]] bool has_attribute_support(uint64_t attr_flag) const noexcept {
        return (stx_.stx_attributes_mask & attr_flag) != 0;
    }

    [[nodiscard]] bool attribute_value(uint64_t attr_flag) const noexcept {
        return (stx_.stx_attributes & attr_flag) != 0;
    }

    void print_timestamp(std::string_view label, const struct statx_timestamp& ts) const {
        std::time_t sec = static_cast<std::time_t>(ts.tv_sec);
        std::tm tm_buf{};
        if (::localtime_r(&sec, &tm_buf) != nullptr) {
            std::cout << "  " << std::left << std::setw(18) << label << ": "
                      << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S") << "."
                      << std::setfill('0') << std::setw(9) << ts.tv_nsec << " нс\n"
                      << std::setfill(' ');
        } else {
            std::cout << "  " << label << ": " << ts.tv_sec << " с\n";
        }
    }

    void print_all() const {
        std::cout << "Розмір файлу        : " << size() << " байтів\n";
        std::cout << "Номер Inode         : " << inode() << "\n";
        std::cout << "Кількість посилань  : " << nlink() << "\n";
        std::cout << "Права доступу       : 0" << std::oct << permissions() << std::dec << "\n\n";

        std::cout << "--- Часові позначки ---\n";
        if (has_field(STATX_ATIME)) print_timestamp("Доступ (atime)", stx_.stx_atime);
        if (has_field(STATX_MTIME)) print_timestamp("Модифікація (mtime)", stx_.stx_mtime);
        if (has_field(STATX_CTIME)) print_timestamp("Зміна inode (ctime)", stx_.stx_ctime);

        if (has_field(STATX_BTIME)) {
            print_timestamp("Створення (btime)", stx_.stx_btime);
        } else {
            std::cout << "  Створення (btime): [НЕ ПІДТРИМУЄТЬСЯ ФАЙЛОВОЮ СИСТЕМОЮ]\n";
        }

        std::cout << "\n--- Розширені атрибути (stx_attributes) ---\n";
        check_and_print_attr("Immutable (+i)", STATX_ATTR_IMMUTABLE);
        check_and_print_attr("Append-only (+a)", STATX_ATTR_APPEND);
        check_and_print_attr("Compressed", STATX_ATTR_COMPRESSED);
        check_and_print_attr("Encrypted", STATX_ATTR_ENCRYPTED);
#ifdef STATX_ATTR_VERITY
        check_and_print_attr("fs-verity", STATX_ATTR_VERITY);
#endif
#ifdef STATX_ATTR_DAX
        check_and_print_attr("DAX (Direct Acc)", STATX_ATTR_DAX);
#endif

#ifdef STATX_DIOALIGN
        std::cout << "\n--- Параметри вирівнювання O_DIRECT (STATX_DIOALIGN) ---\n";
        if (has_field(STATX_DIOALIGN)) {
            std::cout << "  Вирівнювання буфера пам'яті : " << stx_.stx_dio_mem_align << " байтів\n";
            std::cout << "  Вирівнювання зсуву у файлі  : " << stx_.stx_dio_offset_align << " байтів\n";
        } else {
            std::cout << "  Вирівнювання O_DIRECT       : [НЕ ПІДТРИМУЄТЬСЯ ЯДРОМ ТА ФС]\n";
        }
#endif
    }

private:
    struct statx stx_{};

    void check_and_print_attr(std::string_view name, uint64_t flag) const {
        if (has_attribute_support(flag)) {
            std::cout << "  " << std::left << std::setw(18) << name << ": "
                      << (attribute_value(flag) ? "ТАК" : "НІ") << "\n";
        }
    }
};

} // namespace fs_inspect

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_файлу>\n";
        return EXIT_FAILURE;
    }

    try {
        unsigned int extra_mask = 0;
#ifdef STATX_DIOALIGN
        extra_mask |= STATX_DIOALIGN;
#endif
        auto info = fs_inspect::StatxInfo::fetch(argv[1], extra_mask);
        std::cout << "=== Інспектування файлу (C++): " << argv[1] << " ===\n";
        info.print_all();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

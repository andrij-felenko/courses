// C++ форматування підсумкової статистики scrub
#include <iostream>
#include <linux/btrfs.h>

inline void printScrubProgress(const btrfs_scrub_progress& p) {
    std::cout << "--- Статистика цілісності Btrfs Scrub ---\n"
              << "Проскановано даних: " << (p.data_bytes_scrubbed / (1024 * 1024)) << " МіБ\n"
              << "Проскановано метаданих: " << (p.tree_bytes_scrubbed / (1024 * 1024)) << " МіБ\n"
              << "Апаратних помилок читання: " << p.read_errors << "\n"
              << "Помилок хешу CRC32c: " << p.csum_errors << "\n"
              << "Виправлено з RAID: " << p.corrected_errors << "\n"
              << "НЕВІДНОВЛЮВАНИХ помилок: " << p.uncorrectable_errors << std::endl;
}

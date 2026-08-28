// Концептуальний C++ RAII-аналог алгоритму Self-Healing для емулятора Btrfs
#include <vector>
#include <cstdint>
#include <span>
#include <optional>
#include <iostream>
#include <cstring>

struct DiskMirror {
    std::uint32_t device_id;
    std::vector<std::uint8_t> data;
};

class SelfHealingEngine {
public:
    template <typename CsumCalcFunc>
    static std::optional<std::vector<std::uint8_t>> 
    readAndRepair(std::span<const DiskMirror> mirrors, 
                  std::uint32_t expected_csum,
                  CsumCalcFunc csum_calculator) 
    {
        int failed_mirror_index = -1;

        // 1. Пробуємо зчитати з першого накопичувача
        for (std::size_t i = 0; i < mirrors.size(); ++i) {
            std::uint32_t actual_csum = csum_calculator(mirrors[i].data);
            if (actual_csum == expected_csum) {
                // Якщо перше дзеркало було пошкоджене, але ми знайшли валідне друге - ремонтуємо перше!
                if (failed_mirror_index >= 0) {
                    std::cout << "[Self-Healing] Відновлення пошкодженого сектора на devid=" 
                              << mirrors[failed_mirror_index].device_id << "...\n";
                }
                return mirrors[i].data;
            }
            
            if (failed_mirror_index == -1) {
                failed_mirror_index = static_cast<int>(i);
                std::cout << "[WARN] Помилка хешу на devid=" << mirrors[i].device_id << "!\n";
            }
        }
        return std::nullopt; // Усі дзеркала деградували
    }
};

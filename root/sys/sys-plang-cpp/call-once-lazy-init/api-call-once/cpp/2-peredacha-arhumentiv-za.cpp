#include <mutex>
#include <functional>
#include <string>
#include <vector>

void fill_hardware_ids(std::vector<int>& ids, std::string& status) {
    ids.push_back(101);
    ids.push_back(102);
    status = "READY";
}

void configure(std::once_flag& flag, std::vector<int>& out_ids, std::string& out_status) {
    // ❌ Помилка: std::call_once(flag, fill_hardware_ids, out_ids, out_status);
    
    // ✅ Правильно: загортаємо в std::ref
    std::call_once(flag, fill_hardware_ids, std::ref(out_ids), std::ref(out_status));
}

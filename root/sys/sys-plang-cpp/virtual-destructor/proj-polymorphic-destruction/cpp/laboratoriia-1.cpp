#include <iostream>
#include <memory>
#include <vector>
#include <cstring>

class BaseService {
public:
    void serve() { /* базовий цикл обробки */ }
    // Помилка: деструктор залишено невіртуальним за замовчуванням
    ~BaseService() = default;
};

class HeavyStreamingService : public BaseService {
    char* dynamic_payload{nullptr};
    std::size_t payload_size{0};
    std::vector<int> active_sessions;

public:
    HeavyStreamingService(std::size_t size)
        : payload_size(size), active_sessions(1000, 1) {
        dynamic_payload = new char[payload_size];
        std::memset(dynamic_payload, 0x55, payload_size);
        std::cout << "[+] HeavyStreamingService створено: " << payload_size << " байтів у купі\n";
    }

    ~HeavyStreamingService() {
        delete[] dynamic_payload;
        std::cout << "[-] HeavyStreamingService успішно зруйновано\n";
    }
};

int main() {
    std::cout << "=== Старт тесту: видалення через BaseService* ===\n";
    BaseService* service = new HeavyStreamingService(1024 * 1024); // 1 МБ
    
    // Поліморфне видалення через покажчик на базу
    delete service;
    
    std::cout << "=== Завершення main() ===\n";
    return 0;
}

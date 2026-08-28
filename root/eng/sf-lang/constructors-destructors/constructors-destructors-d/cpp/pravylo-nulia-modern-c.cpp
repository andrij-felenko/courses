#include <string>
#include <vector>
#include <memory>

// Правило нуля: клас не оголошує жодної спеціальної функції.
// Компілятор сам генерує правильні деструктор, копіювання та переміщення.
class UserProfile {
    std::string username_;
    std::vector<int> permissions_;
    std::unique_ptr<int[]> cache_buffer_; // unique_ptr автоматично забороняє некоректне
                                          // копіювання й дозволяє коректне переміщення
public:
    UserProfile(std::string name)
        : username_(std::move(name)), cache_buffer_(std::make_unique<int[]>(256)) {}
};

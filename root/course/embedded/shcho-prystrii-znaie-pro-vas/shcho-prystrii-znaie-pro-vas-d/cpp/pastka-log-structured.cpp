// Оновлення пароля Wi-Fi через ідіоматичний C++ інтерфейс NVS
#include <memory>
#include <string_view>

class NvsStorage {
public:
    explicit NvsStorage(std::string_view ns) noexcept {
        // Ініціалізація дескриптора NVS
    }
    
    bool setString(std::string_view key, std::string_view value) noexcept {
        // Запис нового значення у лог NVS
        return true;
    }
};

void updateCredentials(std::string_view newPass) {
    NvsStorage storage("storage");
    storage.setString("wifi_pass", newPass);
}

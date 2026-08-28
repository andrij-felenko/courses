#include <shared_mutex>
#include <string>
#include <unordered_map>

class PhoneBook {
    mutable std::shared_mutex rw_mtx_;
    std::unordered_map<std::string, std::string> contacts_;

public:
    // Багато ниток можуть читати телефонну книгу одночасно!
    std::string find_number(const std::string& name) const {
        std::shared_lock<std::shared_mutex> lock(rw_mtx_);
        auto it = contacts_.find(name);
        return (it != contacts_.end()) ? it->second : "";
    }

    // Тільки один писець має ексклюзивний доступ для додавання запису
    void add_contact(const std::string& name, const std::string& number) {
        std::scoped_lock lock(rw_mtx_); // Ексклюзивне захоплення
        contacts_[name] = number;
    }
};

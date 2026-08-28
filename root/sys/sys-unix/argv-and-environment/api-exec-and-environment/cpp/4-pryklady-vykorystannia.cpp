// Приклад на мові C++20: RAII-обгортка для формування середовища та запуску
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span >
#include <system_error>
#include <unistd.h>
#include <sys/auxv.h>

class EnvironmentContainer {
public:
    void add_variable(std::string_view key, std::string_view value) {
        std::string entry;
        entry.reserve(key.size() + 1 + value.size());
        entry.append(key).append("=").append(value);
        storage_.push_back(std::move(entry));
    }

    [[nodiscard]] std::vector<char*> get_c_pointers() {
        std::vector<char*> pointers;
        pointers.reserve(storage_.size() + 1);
        for (auto& str : storage_) {
            pointers.push_back(str.data());
        }
        pointers.push_back(nullptr);
        return pointers;
    }

private:
    std::vector<std::string> storage_;
};

int main() {
    // Зчитування auxv через C++ API
    auto page_size = getauxval(AT_PAGESZ);
    auto secure_mode = getauxval(AT_SECURE);

    std::cout << "=== C++ Process Bootstrap Info ===\n";
    std::cout << "Page Size: " << page_size << " bytes\n";
    std::cout << "AT_SECURE: " << secure_mode << "\n\n";

    EnvironmentContainer env_box;
    env_box.add_variable("PATH", "/usr/bin:/bin");
    env_box.add_variable("APP_MODE", "PRODUCTION");
    env_box.add_variable("CPP_VERSION", "202002L");

    auto envp = env_box.get_c_pointers();

    std::vector<std::string> arg_strings = {"env"};
    std::vector<char*> argv = {arg_strings[0].data(), nullptr};

    ::execve("/usr/bin/env", argv.data(), envp.data());

    // Обробка помилок
    int error_code = errno;
    std::system_error sys_err(error_code, std::generic_category());
    std::cerr << "Execution failed: " << sys_err.what() << '\n';

    return EXIT_FAILURE;
}

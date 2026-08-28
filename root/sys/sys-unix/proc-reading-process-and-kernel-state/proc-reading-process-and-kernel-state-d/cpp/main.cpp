#include <iostream>
#include <fstream>
#include <filesystem>
#include <system_error>

class SysctlManager {
public:
    static bool setIpForwarding(bool enable) {
        const std::filesystem::path path{"/proc/sys/net/ipv4/ip_forward"};
        std::ofstream file(path);
        if (!file.is_open()) {
            std::cerr << "Помилка доступу до " << path << "\n";
            return false;
        }
        file << (enable ? 1 : 0) << "\n";
        return file.good();
    }
};

int main() {
    if (SysctlManager::setIpForwarding(true)) {
        std::cout << "IP forwarding успішно увімкнено.\n";
    }
    return 0;
}

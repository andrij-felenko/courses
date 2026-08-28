#include <iostream>
#include <chrono>
#include <ctime>
#include <iomanip>

int main() {
    const auto now = std::chrono::system_clock::now();
    const std::time_t now_c = std::chrono::system_clock::to_time_t(now);

    std::tm tm_utc{}, tm_local{};
    gmtime_r(&now_c, &tm_utc);
    localtime_r(&now_c, &tm_local);

    std::cout << "time_t          : " << now_c << '\n';
    std::cout << "UTC час         : " << std::put_time(&tm_utc, "%Y-%m-%d %H:%M:%S %Z") << '\n';
    std::cout << "Локальний час   : " << std::put_time(&tm_local, "%Y-%m-%d %H:%M:%S %Z (UTC%z)") << '\n';
    std::cout << "Літній час (DST): " << (tm_local.tm_isdst > 0 ? "ТАК" : "НІ") << '\n';

    return 0;
}

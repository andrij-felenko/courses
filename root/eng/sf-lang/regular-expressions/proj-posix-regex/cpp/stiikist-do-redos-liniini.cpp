#include <iostream>
#include <chrono>
#include <string>
#include <string_view>
#include <future>
#include <regex>

// Захист від зависання бектрекінг-рушія шляхом контролю таймауту в C++
bool match_with_timeout(std::string_view pattern_str, std::string_view input_str,
                        std::chrono::milliseconds timeout) {
    std::string pat(pattern_str);
    std::string text(input_str);

    // Запуск зіставлення в окремому асинхронному потоці
    auto task = std::async(std::launch::async, [pat, text]() {
        try {
            std::regex re(pat, std::regex::ECMAScript);
            return std::regex_match(text, re);
        } catch (const std::exception&) {
            return false;
        }
    });

    std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
    std::future_status status = task.wait_for(timeout);

    if (status == std::future_status::ready) {
        auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::steady_clock::now() - start).count();
        std::cout << "std::regex завершився за " << elapsed << " мкс\n";
        return task.get();
    } else {
        std::cout << "УВАГА: Спрацював таймаут! Виявлено катастрофічний бектрекінг (ReDoS).\n";
        return false;
    }
}

int main() {
    std::string_view redos_pattern = "^(a+)+$";
    std::string_view evil_input = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!";

    std::cout << "Тестування std::regex під захисним таймаутом 200 мс:\n";
    match_with_timeout(redos_pattern, evil_input, std::chrono::milliseconds(200));
    return 0;
}

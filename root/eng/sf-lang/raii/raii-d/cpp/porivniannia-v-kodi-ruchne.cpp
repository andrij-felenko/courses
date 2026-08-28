#include <mutex>
#include <vector>
#include <fstream>
#include <stdexcept>

std::mutex log_mutex;

void write_log_entry(const std::string& message) {
    // 1. Захоплення блокування через RAII
    std::lock_guard<std::mutex> lock(log_mutex);

    // 2. Захоплення файлового дескриптора через RAII
    std::ofstream file("app.log", std::ios::app);
    if (!file.is_open()) {
        // Ранній вихід: mtx автоматично розблокується деструктором lock
        throw std::runtime_error("Не вдалося відкрити файл журналу");
    }

    // 3. Захоплення динамічної пам'яті через RAII-контейнер
    std::vector<char> buffer(message.begin(), message.end());

    if (buffer.empty()) {
        // Ранній return: file закриється, lock розблокує м'ютекс
        return;
    }

    file.write(buffer.data(), static_cast<std::streamsize>(buffer.size()));
    file.put('\n');

    // Успішний вихід: усе звільняється компілятором у строгому порядку LIFO:
    // 1. ~vector() звільняє купу
    // 2. ~ofstream() закриває файл
    // 3. ~lock_guard() відпускає м'ютекс
}

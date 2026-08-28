#include <iostream>
#include <string>

// Міксин логування: приймає базовий клас як параметр шаблону
template <typename BaseClass>
class LoggingMixin : public BaseClass {
public:
    template <typename... Args>
    LoggingMixin(Args&&... args) : BaseClass(std::forward<Args>(args)...) {}

    void executeWithLog() {
        std::cout << "[LOG] Початок виконання операції\n";
        this->execute(); // Викликає метод базового класу
        std::cout << "[LOG] Операцію завершено\n";
    }
};

class Task {
public:
    void execute() {
        std::cout << "Виконуються корисні обчислення...\n";
    }
};

// Лінеаризація під час компіляції: LoggingTask є нащадком Task
using LoggingTask = LoggingMixin<Task>;

int main() {
    LoggingTask task;
    task.executeWithLog();
    return 0;
}

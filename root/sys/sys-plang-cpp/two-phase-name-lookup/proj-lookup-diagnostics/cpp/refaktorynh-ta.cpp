#include <iostream>

// КРОК 1: Попереднє оголошення незалежної функції для Фази 1
void log_step_code(int code);

// КРОК 2: Визначення шаблону
template <typename T>
void execute_workflow(T data) {
    log_step_code(100);        // Успішно зв'язується на Фазі 1
    process_custom_data(data); // Зв'язується на Фазі 2 через ADL
}

// Реалізація незалежної функції
void log_step_code(int code) {
    std::cout << "Step code: " << code << "\n";
}

namespace app {
    struct DataPayload {};
    void process_custom_data(DataPayload) {
        std::cout << "App data payload processed via ADL\n";
    }
}

int main() {
    app::DataPayload payload;
    execute_workflow(payload); // Збірка й виконання пройдуть ідеально!
}

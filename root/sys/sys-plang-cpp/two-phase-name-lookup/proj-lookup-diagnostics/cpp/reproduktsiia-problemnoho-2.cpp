#include <iostream>

// 1. Оголошення шаблону обробки
template <typename T>
void execute_workflow(T data) {
    // Виклик 1: 100 є значенням типу int — це НЕЗАЛЕЖНИЙ вирази!
    log_step_code(100);

    // Виклик 2: data має тип T — це ЗАЛЕЖНИЙ вираз!
    process_custom_data(data);
}

// 2. Функція для незалежного виклику оголошена ПІСЛЯ шаблону
void log_step_code(int code) {
    std::cout << "Step code: " << code << "\n";
}

namespace app {
    struct DataPayload {};

    // 3. Функція для залежного виклику у просторі користувача
    void process_custom_data(DataPayload) {
        std::cout << "App data payload processed\n";
    }
}

int main() {
    app::DataPayload payload;
    // execute_workflow(payload); // ПОМИЛКА під час компіляції!
}

#include <iostream>
#include <cstdint>

int32_t generate_transaction_id() noexcept {
    // Область видимості: локальна (тільки всередині generate_transaction_id)
    // Тривалість життя: статична (зберігається в сегменті .data на весь час процесу)
    static int32_t s_id_counter = 1000;
    return ++s_id_counter;
}

int main() {
    std::cout << "ID 1: " << generate_transaction_id() << '\n'; // 1001
    std::cout << "ID 2: " << generate_transaction_id() << '\n'; // 1002

    // Помилка компіляції: s_id_counter недоступний за межами функції
    // s_id_counter = 0;
    return 0;
}

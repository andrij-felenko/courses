void test_1_reallocation_trap() {
    std::cout << "\n--- Сценарій 1: Інвалідація через push_back під час реалокації ---\n";
    CheckedVector<int> vec = {10, 20, 30};

    auto it = vec.begin();
    std::cout << "Створено ітератор на elem 0: " << *it << " (епоха ітератора: " << it.created_epoch() << ")\n";

    std::cout << "Виконуємо push_back(40), що змінює епоху контейнера до " << vec.epoch() + 1 << "...\n";
    vec.push_back(40);

    try {
        std::cout << "Спроба прочитати значення через старий ітератор: ";
        std::cout << *it << "\n";
    } catch (const std::exception& e) {
        std::cout << "УСПІШНО ВИЯВЛЕНО ПОМИЛКУ: " << e.what() << "\n";
    }
}

void test_2_invalid_erase_loop() {
    std::cout << "\n--- Сценарій 2: Помилка некоректного видалення елементів у циклі ---\n";
    CheckedVector<int> vec = {1, 2, 3, 4, 5};

    try {
        for (auto it = vec.begin(); it != vec.end(); ++it) {
            if (*it % 2 == 0) {
                std::cout << "Видаляємо парне число " << *it << "...\n";
                vec.erase(it); // Метод erase збільшує епоху!
            }
        }
    } catch (const std::exception& e) {
        std::cout << "УСПІШНО ВИЯВЛЕНО ПОМИЛКУ В ЦИКЛІ: " << e.what() << "\n";
    }
}

void test_3_correct_iterator_update() {
    std::cout << "\n--- Сценарій 3: Коректне видалення з оновленням ітератора ---\n";
    CheckedVector<int> vec = {1, 2, 3, 4, 5, 6};

    auto it = vec.begin();
    while (it != vec.end()) {
        if (*it % 2 == 0) {
            // Метод erase повертає новий ітератор з актуальною епохою!
            it = vec.erase(it);
        } else {
            ++it;
        }
    }

    std::cout << "Результат успішного видалення: ";
    for (auto val : vec) {
        std::cout << val << " ";
    }
    std::cout << "\nУсі операції виконано без помилок!\n";
}

int main() {
    test_1_reallocation_trap();
    test_2_invalid_erase_loop();
    test_3_correct_iterator_update();
    return 0;
}

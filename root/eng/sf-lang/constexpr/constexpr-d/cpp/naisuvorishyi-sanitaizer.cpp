constexpr int get_element(int index) {
    int arr[4] = {10, 20, 30, 40};
    return arr[index]; // Якщо index >= 4 — це вихід за межі!
}

// Перевірка коректного індексу
static_assert(get_element(2) == 30); // Успішно!

// Спроба викликати з помилковим індексом
constexpr int bad = get_element(5); // ПОМИЛКА КОМПІЛЯЦІЇ!

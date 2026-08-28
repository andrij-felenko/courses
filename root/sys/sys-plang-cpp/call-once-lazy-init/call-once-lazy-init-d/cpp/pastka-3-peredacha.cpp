// ❌ ПОМИЛКА компіляції або зміна тимчасової копії
void populate_data(std::vector<int>& out_vec) {
    out_vec.push_back(42);
}

void run(std::once_flag& flag, std::vector<int>& vec) {
    // ❌ Помилка: std::call_once(flag, populate_data, vec);
    // ✅ Правильно: використовуємо std::ref для збереження семантики посилання
    std::call_once(flag, populate_data, std::ref(vec));
}

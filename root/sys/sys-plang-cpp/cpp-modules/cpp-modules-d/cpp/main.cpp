// --- Файл: main.cpp ---
import session_manager;

int main() {
    // 1. Спроба прямого оголошення за назвою типу:
    // UserSession s; // ❌ ПОМИЛКА: ідентифікатор 'UserSession' не знайдено (Not Visible)

    // 2. Отримання через фабрику за допомогою auto:
    auto session = create_session(42); // ✅ ПРАЦЮЄ: тип UserSession досяжний (Reachable)

    // 3. Виклик методів об'єкта:
    if (session.is_valid()) {          // ✅ ПРАЦЮЄ: зміщення методу відоме компілятору з BMI
        session.terminate();
    }

    // 4. Обчислення розміру об'єкта:
    constexpr size_t sz = sizeof(session); // ✅ ПРАЦЮЄ: точний розмір типу зафіксовано в BMI
}

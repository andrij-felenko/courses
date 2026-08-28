#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Session {
    int id;
    std::string name;
};

int main() {
    std::vector<Session> sessions;
    sessions.reserve(2);
    sessions.push_back({101, "AdminAuth"});
    sessions.push_back({102, "UserGuest"});

    // Зберігаємо посилання на перший елемент
    const Session& primary = sessions[0];

    // Додавання третього елемента перевищує reserve(2) і спричиняє релокацію буфера
    sessions.push_back({103, "ServiceWorker"});

    // Помилка: primary дивиться на старий звільнений буфер (Heap-Use-After-Free)
    std::cout << "Сесія ID: " << primary.id << ", Назва: " << primary.name << '\n';

    return 0;
}

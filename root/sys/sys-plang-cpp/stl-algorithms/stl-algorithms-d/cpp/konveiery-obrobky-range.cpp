#include <ranges>
#include <iostream>
#include <vector>

struct User {
    std::string name;
    int         score;
    bool        active;
};

void process_users(const std::vector<User>& users) {
    // Будуємо лінивий конвеєр: фільтрація активних -> проєкція score -> вибірка перших 3
    auto view = users 
              | std::views::filter(&User::active)
              | std::views::transform(&User::score)
              | std::views::take(3);

    for (int score : view) {
        std::cout << "Top score: " << score << "\n";
    }
}

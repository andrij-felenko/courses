#include <iostream>
#include <vector>
#include <algorithm>

struct CoinCount {
    int denomination;
    int count;
};

// Функція жадібного розміну суми amount
std::vector<CoinCount> minCoinsGreedy(int amount, std::vector<int>& coins) {
    if (amount <= 0 || coins.empty()) {
        return {};
    }

    // Крок 1: Сортування номіналів за спаданням
    std::sort(coins.rbegin(), coins.rend());

    std::vector<CoinCount> result;
    int currentAmount = amount;

    // Крок 2: Жадібний вибір найбільшого номіналу
    for (int coin : coins) {
        if (currentAmount == 0) {
            break;
        }
        if (coin <= currentAmount) {
            int count = currentAmount / coin;
            currentAmount %= coin;
            result.push_back({coin, count});
        }
    }

    // Якщо залишилася невидана решта — система не дає розшити суму цілком
    if (currentAmount > 0) {
        return {}; // Неможливо видати точну суму
    }

    return result;
}

int main() {
    std::vector<int> denominations = {1, 2, 5, 10, 20, 50, 100, 200, 500};
    int targetAmount = 878;

    std::vector<CoinCount> change = minCoinsGreedy(targetAmount, denominations);

    std::cout << "Розмін суми " << targetAmount << ":\n";
    int totalCoins = 0;
    for (const auto& item : change) {
        std::cout << "  Монета " << item.denomination << " грн: " << item.count << " шт.\n";
        totalCoins += item.count;
    }
    std::cout << "Загальна кількість монет: " << totalCoins << "\n";

    return 0;
}

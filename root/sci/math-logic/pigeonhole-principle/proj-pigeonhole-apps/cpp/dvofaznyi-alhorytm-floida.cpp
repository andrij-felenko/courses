#include <iostream>
#include <vector>
#include <span >

int find_duplicate_floyd(std::span<const int> arr) {
    if (arr.size() <= 1) return -1;

    // Фаза 1: Детекція циклу за допомогою двох швидкостей
    int slow = arr[0];
    int fast = arr[arr[0]];

    while (slow != fast) {
        slow = arr[slow];
        fast = arr[arr[fast]];
    }

    // Фаза 2: Зближення від початку масиву та з точки зустрічі
    fast = 0;
    while (slow != fast) {
        slow = arr[slow];
        fast = arr[fast];
    }

    return slow;
}

int main() {
    const std::vector<int> numbers = { 3, 1, 3, 4, 2, 5 };
    int dup = find_duplicate_floyd(numbers);
    std::cout << "Елемент-дублікат за принципом Діріхле: " << dup << "\n";
    return 0;
}

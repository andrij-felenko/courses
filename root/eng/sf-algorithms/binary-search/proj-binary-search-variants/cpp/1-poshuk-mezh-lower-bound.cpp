#include <iostream>
#include <vector>

// lower_bound: повертає найменший індекс i такий, що arr[i] >= target
int lower_bound(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = arr.size(); // Напіввідкритий інтервал [low, high)

    while (low < high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] >= target) {
            high = mid; // Звужуємо праворуч, зберігаючи потенційний кандидат mid
        } else {
            low = mid + 1; // arr[mid] < target, тому шукаємо строго праворуч
        }
    }
    return low; // low вказує на перший елемент >= target
}

// upper_bound: повертає найменший індекс i такий, що arr[i] > target
int upper_bound(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = arr.size(); // Напіввідкритий інтервал [low, high)

    while (low < high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] > target) {
            high = mid; // Звужуємо праворуч
        } else {
            low = mid + 1; // arr[mid] <= target, продовжуємо пошук праворуч
        }
    }
    return low; // low вказує на перший елемент > target
}

int main() {
    std::vector<int> data = {1, 2, 2, 2, 3, 5, 8};
    int target = 2;

    int lb = lower_bound(data, target);
    int ub = upper_bound(data, target);

    std::cout << "lower_bound (>= 2): index " << lb << " (значення " << data[lb] << ")\n";
    std::cout << "upper_bound (> 2):  index " << ub << " (значення " << data[ub] << ")\n";
    std::cout << "Кількість елементів = " << (ub - lb) << "\n";

    return 0;
}

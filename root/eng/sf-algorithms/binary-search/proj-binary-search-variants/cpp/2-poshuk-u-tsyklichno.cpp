#include <iostream>
#include <vector>

int search_rotated(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = arr.size() - 1;

    while (low <= high) {
        int mid = low + (high - low) / 2;

        if (arr[mid] == target) {
            return mid;
        }

        // Перевіряємо, чи впорядкована ліва частина
        if (arr[low] <= arr[mid]) {
            // target лежить у відсортованому лівому сегменті
            if (arr[low] <= target && target < arr[mid]) {
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        } 
        // Інакше впорядкована права частина
        else {
            // target лежить у відсортованому правому сегменті
            if (arr[mid] < target && target <= arr[high]) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
    }
    return -1; // Не знайдено
}

int main() {
    std::vector<int> rotated = {4, 5, 6, 7, 0, 1, 2};
    int target = 0;
    int idx = search_rotated(rotated, target);

    std::cout << "Елемент " << target << " знайдено на індексі: " << idx << "\n";
    return 0;
}

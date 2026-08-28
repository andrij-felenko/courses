#include <iostream>
#include <vector>
#include <numeric>
#include <random>
#include <algorithm>

struct FlashCell {
    int value;
    static inline size_t write_count = 0;

    FlashCell& operator=(int val) {
        if (value != val) {
            value = val;
            write_count++;
        }
        return *this;
    }

    FlashCell& operator=(const FlashCell& other) {
        if (this != &other && value != other.value) {
            value = other.value;
            write_count++;
        }
        return *this;
    }

    bool operator<(const FlashCell& other) const {
        return value < other.value;
    }
};

void run_write_benchmark() {
    const size_t N = 100;
    std::vector<int> raw_data(N);
    std::iota(raw_data.begin(), raw_data.end(), 1);
    
    std::mt19937 g(42);
    std::shuffle(raw_data.begin(), raw_data.end(), g);

    // 1. Selection Sort
    std::vector<FlashCell> arr1(N);
    for (size_t i = 0; i < N; ++i) arr1[i].value = raw_data[i];
    FlashCell::write_count = 0;

    for (size_t i = 0; i < N - 1; ++i) {
        size_t min_idx = i;
        for (size_t j = i + 1; j < N; ++j) {
            if (arr1[j] < arr1[min_idx]) min_idx = j;
        }
        if (min_idx != i) {
            std::swap(arr1[i], arr1[min_idx]);
        }
    }
    size_t sel_writes = FlashCell::write_count;

    // 2. Insertion Sort
    std::vector<FlashCell> arr2(N);
    for (size_t i = 0; i < N; ++i) arr2[i].value = raw_data[i];
    FlashCell::write_count = 0;

    for (size_t i = 1; i < N; ++i) {
        FlashCell key = arr2[i];
        int j = static_cast<int>(i) - 1;
        while (j >= 0 && key < arr2[j]) {
            arr2[j + 1] = arr2[j];
            j--;
        }
        arr2[j + 1] = key;
    }
    size_t ins_writes = FlashCell::write_count;

    std::cout << "--- Результати тестування операцій запису (N = 100) ---\n";
    std::cout << "Selection Sort перезаписів у пам'ять: " << sel_writes << "\n";
    std::cout << "Insertion Sort перезаписів у пам'ять: " << ins_writes << "\n";
}

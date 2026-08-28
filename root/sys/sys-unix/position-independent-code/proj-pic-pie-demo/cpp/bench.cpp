// bench.cpp — C++ вимірювання часу викликів
#include <iostream>
#include <chrono>

static inline void local_func(long long& val) {
    val++;
}

int main() {
    long long count = 0;
    auto start = std::chrono::high_resolution_clock::now();
    
    for (long long i = 0; i < 100000000LL; i++) {
        local_func(count);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    
    std::cout << "Локальний виклик C++: " << diff.count() << " сек\n";
    return 0;
}

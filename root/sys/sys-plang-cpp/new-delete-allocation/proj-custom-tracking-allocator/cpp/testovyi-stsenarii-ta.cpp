#include <vector>
#include <memory>

struct alignas(64) HeavyVectorData {
    float values[16];
};

void run_test_workload() {
    std::printf("1. Виконання коректних виділень через std::make_unique...\n");
    auto p1 = std::make_unique<int>(100);
    auto p2 = std::make_unique<HeavyVectorData>();

    std::printf("2. Виділення динамічного вектора (STL)...\n");
    std::vector<int> numbers;
    for (int i = 0; i < 500; ++i) {
        numbers.push_back(i);
    }

    std::printf("3. Імітація помилки: непарний new[] / delete...\n");
    int* bad_array = new int[10];
    operator delete(bad_array); // Замість delete[]

    std::printf("4. Імітація помилки: вихід за межі масиву (Buffer Overrun)...\n");
    char* overrun_buf = new char[16];
    // Навмисний запис за межі 16 байтів руйнує хвостову канарку:
    std::memset(overrun_buf, 0xAA, 20); 
    delete[] overrun_buf;

    std::printf("5. Імітація витоку пам'яті (забутий delete)...\n");
    int* leak_ptr = new int(999);
    (void)leak_ptr;
}

int main() {
    run_test_workload();
    MemoryTracker::print_report();
    return 0;
}

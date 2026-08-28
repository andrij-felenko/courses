#include <iostream>
#include <vector>
#include <memory>

void heap_overflow_demo() {
    auto array = std::make_unique<int[]>(5);
    // При прямому індексуванні через сирий покажчик без перевірки меж:
    int* raw_ptr = array.get();
    raw_ptr[5] = 100; // ASan фіксує Heap Buffer Overflow
}

void use_after_free_demo() {
    int* dangling_ptr = nullptr;
    {
        auto temp_obj = std::make_unique<int>(42);
        dangling_ptr = temp_obj.get();
    } // temp_obj виходить з області видимості та звільняє пам'ять
    *dangling_ptr = 999; // ASan фіксує Heap Use-After-Free
}

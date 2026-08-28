#include <memory>
#include <cstddef>
#include <cstdint>
#include <iostream>

struct SensorData {
    double timestamp;  // alignof = 8, sizeof = 8
    float values[3];   // 12 байтів + 4 байти padding -> sizeof = 24
};

int main() {
    alignas(std::max_align_t) std::byte storage[256];
    
    void* current_ptr = storage + 3; // навмисно беремо невирівняну адресу (+3 байти від початку)
    std::size_t free_space = sizeof(storage) - 3;
    
    void* aligned_ptr = std::align(
        alignof(SensorData),
        sizeof(SensorData),
        current_ptr,
        free_space
    );
    
    if (aligned_ptr != nullptr) {
        // current_ptr тепер зсунутий на найближчу адресу, кратну 8 (додано 5 байтів padding)
        // free_space зменшено на розмір доданого padding (на 5 байтів)
        SensorData* sensor = ::new (aligned_ptr) SensorData{100.5, {1.0f, 2.0f, 3.0f}};
        
        std::cout << "Об'єкт успішно розміщено за адресою: " << sensor << "\n";
        
        // Звільнення об'єкта
        sensor->~SensorData();
    }
}

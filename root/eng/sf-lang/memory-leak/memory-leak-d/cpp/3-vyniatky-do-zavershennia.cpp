#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

void process_network_packet() {
    throw std::runtime_error("Мережевий тайм-аут");
}

void unsafe_handler() {
    int *raw_array = new int[5000]; // 20 KB у купі
    process_network_packet();        // Генерує виняток!
    delete[] raw_array;              // Ніколи не виконається -> ВИТІК!
}

void safe_handler() {
    // std::unique_ptr гарантує виклик delete[] під час розкрутки стека
    auto safe_array = std::make_unique<int[]>(5000);
    process_network_packet(); // Навіть при винятку пам'ять звільниться!
}

int main() {
    try {
        safe_handler();
    } catch (const std::exception &e) {
        std::cout << "[C++] Виняток оброблено, уся пам'ять безпечно повернута купі.\n";
    }
    return 0;
}

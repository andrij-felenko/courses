// Зчитування BPF-ітератора з користувацького простору (Userspace C++20)
#include <iostream>
#include <fstream>
#include <string>
#include <system_error>

int main()
{
    std::ifstream iter_stream("/sys/fs/bpf/my_task_iter");
    if (!iter_stream.is_open()) {
        std::cerr << "Не вдалося відкрити закріплений BPF-ітератор\n";
        return 1;
    }

    std::string line;
    while (std::getline(iter_stream, line)) {
        std::cout << "[Kernel Iter] " << line << '\n';
    }

    return 0;
}

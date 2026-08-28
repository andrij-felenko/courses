#include <future>
#include <iostream>

int main() {
    // Негайно запускає фонову задачу
    std::future<int> f = std::async(std::launch::async, []() {
        return 7 * 6;
    });

    std::cout << "Результат std::async: " << f.get() << std::endl;
}

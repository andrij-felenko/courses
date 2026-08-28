#include <future>
#include <iostream>
#include <string>

std::future<int> stage1_parse(const std::string& input) {
    return std::async(std::launch::async, [input]() {
        return std::stoi(input);
    });
}

std::future<double> stage2_compute(std::future<int> prev_future) {
    return std::async(std::launch::async, [f = std::move(prev_future)]() mutable {
        int val = f.get(); // Блокується до завершення stage 1
        return val * 3.14159;
    });
}

int main() {
    auto f1 = stage1_parse("100");
    auto f2 = stage2_compute(std::move(f1));

    std::cout << "Конвеєрний результат: " << f2.get() << std::endl;
}

// app/main.cpp
#include <imgproc/filter.h>
#include <vector>
#include <iostream>

int main() {
    std::vector<uint8_t> test_pixels(1024, 128);
    imgproc::Filter::apply_grayscale(test_pixels);
    std::cout << "Роботу програми завершено штатно." << std::endl;
    return 0;
}

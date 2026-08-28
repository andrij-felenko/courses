#include <iostream>
#include <latch>
#include <thread>
#include <vector>
#include <span>
#include <string_view>

void load_textures(std::latch& done) {
    // Симуляція зчитування текстур з SSD
    std::this_thread::sleep_for(std::chrono::milliseconds(80));
    std::cout << "[IO] Текстури завантажено\n";
    done.count_down(); // Декремент без блокування потоку
}

void load_audio(std::latch& done) {
    std::this_thread::sleep_for(std::chrono::milliseconds(40));
    std::cout << "[IO] Аудіобанки декодовано\n";
    done.count_down();
}

void load_geometry(std::latch& done) {
    std::this_thread::sleep_for(std::chrono::milliseconds(120));
    std::cout << "[IO] Геометрію рівнів побудовано\n";
    done.count_down();
}

int main() {
    constexpr ptrdiff_t total_tasks = 3;
    std::latch loading_latch(total_tasks);

    std::jthread t1(load_textures, std::ref(loading_latch));
    std::jthread t2(load_audio, std::ref(loading_latch));
    std::jthread t3(load_geometry, std::ref(loading_latch));

    std::cout << "[Main] Очікування завершення завантаження ресурсів...\n";
    loading_latch.wait(); // Блокується до досягнення нуля

    std::cout << "[Main] Усі підсистеми готові. Запуск ігрового циклу!\n";
    return 0;
}

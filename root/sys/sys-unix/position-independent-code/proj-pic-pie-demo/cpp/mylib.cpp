// mylib.cpp — C++-версія розділюваної бібліотеки з RAII та шаблонами
#include <iostream>
#include <string_view>
#include <memory>

extern "C" {
    int global_counter = 42;

    void internal_func() {
        global_counter++;
    }

    void exported_func(const char* msg) {
        internal_func();
        std::string_view message{msg};
        std::cout << "[mylib cpp] " << message 
                  << " (лічильник: " << global_counter << ")\n";
    }
}

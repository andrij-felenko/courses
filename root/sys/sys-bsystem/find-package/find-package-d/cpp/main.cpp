// src/main.cpp
#include <png.h>
#include <iostream>
#include <memory>
#include <string_view>

struct PngReadDeleter {
    void operator()(png_structp ptr) const noexcept {
        if (ptr) {
            png_destroy_read_struct(&ptr, nullptr, nullptr);
        }
    }
};

using SafePngHandle = std::unique_ptr<png_struct, PngReadDeleter>;

int main() {
    std::cout << "Версія libpng у системі: " 
              << std::string_view(PNG_LIBPNG_VER_STRING) << "\n";
              
    SafePngHandle png_ptr(png_create_read_struct(PNG_LIBPNG_VER_STRING, nullptr, nullptr, nullptr));
    if (!png_ptr) {
        std::cerr << "Не вдалося ініціалізувати структуру png_struct\n";
        return 1;
    }
    
    std::cout << "Структуру libpng успішно створено та захищено через RAII.\n";
    return 0;
}

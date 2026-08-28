// src/main.cpp
#include <png.h>
#include <iostream>
#include <memory>
#include <string_view>
#include <expected>

// RAII обгортка для автоматичного контролю життєвого циклу ресурсів libpng
struct PngContext {
    png_structp png_ptr{nullptr};
    png_infop info_ptr{nullptr};

    PngContext() {
        png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, nullptr, nullptr, nullptr);
        if (png_ptr) {
            info_ptr = png_create_info_struct(png_ptr);
        }
    }

    ~PngContext() {
        if (png_ptr) {
            png_destroy_read_struct(&png_ptr, info_ptr ? &info_ptr : nullptr, nullptr);
        }
    }

    // Забороняємо копіювання ресурсу
    PngContext(const PngContext&) = delete;
    PngContext& operator=(const PngContext&) = delete;

    [[nodiscard]] bool is_valid() const noexcept {
        return png_ptr != nullptr && info_ptr != nullptr;
    }
};

int main() {
    std::cout << "Версія заголовків libpng: " 
              << std::string_view(PNG_LIBPNG_VER_STRING) << "\n";
    std::cout << "Версія бінарного runtime: " 
              << std::string_view(png_get_header_version(nullptr)) << "\n";

    PngContext ctx;
    if (!ctx.is_valid()) {
        std::cerr << "Помилка: не вдалося ініціалізувати контекст libpng через RAII\n";
        return 1;
    }

    std::cout << "Структури libpng успішно ініціалізовано та захищено через RAII.\n";
    return 0;
}

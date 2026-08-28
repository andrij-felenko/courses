#include <cstddef>
#include <cstdlib>
#include <new>
#include <iostream>

// Глобальне перехоплення стандартного operator new
void* operator new(std::size_t size) {
    if (size == 0) {
        size = 1; // Стандарт вимагає повернення унікальної адреси для 0 байтів
    }
    while (true) {
        if (void* ptr = std::malloc(size)) {
            return ptr;
        }
        // Якщо malloc повернув nullptr, перевіряємо наявність new-handler
        std::new_handler handler = std::get_new_handler();
        if (!handler) {
            throw std::bad_alloc();
        }
        handler(); // Спроба звільнити пам'ять і повторити ітерацію виділення
    }
}

// Глобальне перехоплення стандартного operator delete
void operator delete(void* ptr) noexcept {
    std::free(ptr);
}

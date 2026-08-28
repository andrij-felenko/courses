#include <gsl/gsl>

struct IntBuffer {
    gsl::owner<int*> data; // Лінтер вимагає явного delete[] для цього поля
    size_t count;
};

// Функція явно декларує передачу власності через повернене значення
gsl::owner<IntBuffer*> create_buffer_cpp(size_t count) {
    auto buf = new IntBuffer();
    buf->data = new int[count];
    buf->count = count;
    return buf; // Статичний аналізатор перевіряє передачу власності
}

void destroy_buffer_cpp(gsl::owner<IntBuffer*> buf) {
    if (buf) {
        delete[] buf->data; // Звільнення вкладеного ресурсу
        delete buf;         // Звільнення структури
    }
}

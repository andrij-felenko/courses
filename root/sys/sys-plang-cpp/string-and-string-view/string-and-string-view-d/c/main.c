// C: Аналогічна помилка при поверненні вказівника на локальний масив
#include <stdio.h>

const char* create_dangling_pointer(void) {
    char local_buf[64] = "Тимчасові дані в локальній змінній";
    return local_buf; // Небезпека: повернення вказівника на стековий буфер!
}

void dangling_demo_c(void) {
    const char* bad_ptr = create_dangling_pointer();
    // bad_ptr вказує на вивільнений стековий кадр
}

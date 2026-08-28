// foo.cpp — реалізація двох версій однієї функції у C++
#include <iostream>

extern "C" {

// Стара реалізація для сумісності зі старими бінарниками
int foo_process_v1(int x) {
    return x * 10;
}
__asm__(".symver foo_process_v1, foo_process@LIBFOO_1.0");

// Нова реалізація за замовчуванням (@@) для нових збірок
int foo_process_v2(int x, int flags) {
    return x * 10 + flags;
}
__asm__(".symver foo_process_v2, foo_process@@LIBFOO_2.0");

}

#include <iostream>
#include <cstdint>

// Вказівка компілятору запакувати поля без вирівнювання (1 байт)
#pragma pack(push, 1)
struct CompactHeader {
    uint8_t  flag;
    uint32_t data;
};
#pragma pack(pop)

// Застосування _Pragma всередині макросу для ізоляції попереджень
#define SUPPRESS_DEPRECATED_WARNING \
    _Pragma("GCC diagnostic push") \
    _Pragma("GCC diagnostic ignored \"-Wdeprecated-declarations\"")

int main() {
    std::cout << "Розмір CompactHeader: " << sizeof(CompactHeader) << " байтів\n";
    return 0;
}
